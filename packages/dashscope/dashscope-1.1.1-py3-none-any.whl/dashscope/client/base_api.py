import json
import os
import time
from http import HTTPStatus
from typing import List, Union

import aiohttp
import requests

import dashscope
from dashscope.api_entities.api_request_factory import _build_api_request
from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.common.api_key import get_default_api_key
from dashscope.common.constants import (DEFAULT_REQUEST_TIMEOUT_SECONDS,
                                        REPEATABLE_STATUS, TaskStatus)
from dashscope.common.error import InvalidParameter, InvalidTask, ModelRequired
from dashscope.common.logging import logger
from dashscope.common.utils import _handle_http_response, default_headers


def _handle_http_failed_response(
        response: requests.Response) -> DashScopeAPIResponse:
    msg = ''
    code = None
    request_id = ''
    if 'application/json' in response.headers.get('content-type', ''):
        error = response.json()
        if 'message' in error:
            msg = error['message']
        if 'code' in error:
            code = error['code']
        if 'request_id' in error:
            request_id = error['request_id']
        return DashScopeAPIResponse(request_id=request_id,
                                    status_code=response.status_code,
                                    code=code,
                                    message=msg)
    else:
        msg = response.content.decode('utf-8')
        return DashScopeAPIResponse(request_id=request_id,
                                    status_code=response.status_code,
                                    code='Unknown',
                                    message=msg)


def _normalization_url(*args):
    url = dashscope.base_http_api_url
    if not url.endswith('/'):
        url += '/'
    for arg in args:
        url += arg
        url += '/'
    return url[:-1]


class BaseApi():
    """BaseApi, internal use only.

    """
    @classmethod
    def _validate_params(cls, api_key, model):
        if api_key is None:
            api_key = get_default_api_key()
        if model is None or not model:
            raise ModelRequired('Model is required!')
        return api_key, model

    @classmethod
    def call(cls,
             model: str,
             input: object,
             task_group: str,
             task: str = None,
             function: str = None,
             api_key: str = None,
             **kwargs) -> DashScopeAPIResponse:
        """Call service and get result.

        Args:
            model (str): The requested model, such as gpt3-v2
            input (object): The api input data, cannot be None.
            task_group (str, optional): The api task group.
            task (str, optional): The task name. Defaults to None.
            function (str, optional): The function of the task.
                Defaults to None.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.
            api_protocol (str, optional): Api protocol websocket or http.
                Defaults to None.
            ws_stream_mode (str, optional): websocket stream mode,
                [none, in, out, duplex]. Defaults to out.
            is_binary_input (bool, optional): Is input data binary.
                Defaults to False.
            http_method (str, optional): If api protocol is http, specifies
                method[GET, POST]. Defaults to POST.

        Returns:
            DashScopeAPIResponse: The service response.
        """
        api_key, model = BaseApi._validate_params(api_key, model)
        request = _build_api_request(model=model,
                                     input=input,
                                     task_group=task_group,
                                     task=task,
                                     function=function,
                                     api_key=api_key,
                                     **kwargs)
        # call request service.
        return request.call()


class AsyncTaskGetMixin():
    @classmethod
    def _get(cls, task_id: str, api_key: str = None) -> DashScopeAPIResponse:
        status_url = _normalization_url('tasks', task_id)
        with requests.Session() as session:
            logger.debug('Starting request: %s' % status_url)
            response = session.get(status_url,
                                   headers={
                                       **default_headers(api_key),
                                   },
                                   timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS)
            logger.debug('Starting processing response: %s' % status_url)
            return cls._handle_http_response(response)

    @classmethod
    def _handle_http_response(cls, response: requests.Response):
        request_id = ''
        if response.status_code == HTTPStatus.OK:
            output = None
            usage = None
            code = None
            msg = ''
            json_content = response.json()
            if 'code' in json_content:
                code = json_content['code']
            if 'message' in json_content:
                msg = json_content['message']
            if 'output' in json_content:
                output = json_content['output']
            if 'usage' in json_content:
                usage = json_content['usage']
            if 'request_id' in json_content:
                request_id = json_content['request_id']
            return DashScopeAPIResponse(request_id=request_id,
                                        status_code=response.status_code,
                                        code=code,
                                        output=output,
                                        usage=usage,
                                        message=msg)
        else:
            return _handle_http_failed_response(response)


class BaseAsyncApi(AsyncTaskGetMixin):
    """BaseAsyncApi,for async task, internal use only.

    """
    @classmethod
    def _validate_params(cls, api_key, model):
        if api_key is None:
            api_key = get_default_api_key()
        if model is None or not model:
            raise ModelRequired('Model is required!')
        return api_key, model

    @classmethod
    def call(cls, *args, **kwargs) -> DashScopeAPIResponse:
        """Call service and get result.
        """
        task_response = cls.async_call(*args, **kwargs)
        response = cls.wait(task_response)
        return response

    @classmethod
    def _get_task_id(cls, task):
        if isinstance(task, str):
            task_id = task
        elif isinstance(task, DashScopeAPIResponse):
            if task.status_code == HTTPStatus.OK:
                task_id = task.output['task_id']
            else:
                raise InvalidTask('Invalid task, task create failed: %s' %
                                  task)
        else:
            raise InvalidParameter('task invalid!')
        return task_id

    @classmethod
    def cancel(
        cls,
        task: Union[str, DashScopeAPIResponse],
        api_key: str = None,
    ) -> DashScopeAPIResponse:
        """Cancel PENDING task.

        Args:
            task (Union[str, DashScopeAPIResponse]): The task_id, or
                async_call response.
            api_key (str, optional): The api-key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The cancel result.
        """
        task_id = cls._get_task_id(task)
        url = _normalization_url('tasks', task_id, 'cancel')
        with requests.Session() as session:
            response = session.post(url,
                                    headers={
                                        **default_headers(api_key),
                                    })
            if response.status_code == HTTPStatus.OK:
                json_content = response.json()
                request_id = ''
                if 'request_id' in json_content:
                    request_id = json_content['request_id']
                return DashScopeAPIResponse(request_id=request_id,
                                            status_code=response.status_code,
                                            code=None,
                                            output=None,
                                            usage=None,
                                            message='')
            else:
                return _handle_http_failed_response(response)

    @classmethod
    def list(cls,
             start_time: str = None,
             end_time: str = None,
             model_name: str = None,
             api_key_id: str = None,
             region: str = None,
             status: str = None,
             page_no: int = 1,
             page_size: int = 10,
             api_key: str = None,
             **kwargs) -> DashScopeAPIResponse:
        """List async tasks.

        Args:
            start_time (str, optional): The tasks start time,
                for example: 20230420000000. Defaults to None.
            end_time (str, optional): The tasks end time,
                for example: 20230420000000. Defaults to None.
            model_name (str, optional): The tasks model name. Defaults to None.
            api_key_id (str, optional): The tasks api-key-id. Defaults to None.
            region (str, optional): The service region,
                for example: cn-beijing. Defaults to None.
            status (str, optional): The status of tasks[PENDING,
                RUNNING, SUCCEEDED, FAILED, CANCELED]. Defaults to None.
            page_no (int, optional): The page number. Defaults to 1.
            page_size (int, optional): The page size. Defaults to 10.
            api_key (str, optional): The user api-key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The response data.
        """
        url = _normalization_url('tasks')
        params = {'page_no': page_no, 'page_size': page_size}
        if start_time is not None:
            params['start_time'] = start_time
        if end_time is not None:
            params['end_time'] = end_time
        if model_name is not None:
            params['model_name'] = model_name
        if api_key_id is not None:
            params['api_key_id'] = api_key_id
        if region is not None:
            params['region'] = region
        if status is not None:
            params['status'] = status

        with requests.Session() as session:
            response = session.get(url,
                                   params=params,
                                   headers={
                                       **default_headers(api_key),
                                   })
            if response.status_code == HTTPStatus.OK:
                json_content = response.json()
                request_id = ''
                if 'request_id' in json_content:
                    request_id = json_content['request_id']
                    json_content.pop('request_id')
                return DashScopeAPIResponse(request_id=request_id,
                                            status_code=response.status_code,
                                            code=None,
                                            output=json_content,
                                            usage=None,
                                            message='')
            else:
                return _handle_http_failed_response(response)

    @classmethod
    def fetch(
        cls,
        task: Union[str, DashScopeAPIResponse],
        api_key: str = None,
    ) -> DashScopeAPIResponse:
        """Query async task status.

        Args:
            task (Union[str, DashScopeAPIResponse]): The task_id, or
                async_call response.
            api_key (str, optional): The api_key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The async task information.
        """
        task_id = cls._get_task_id(task)
        return cls._get(task_id, api_key)

    @classmethod
    def wait(
        cls,
        task: Union[str, DashScopeAPIResponse],
        api_key: str = None,
    ) -> DashScopeAPIResponse:
        """Wait for async task completion and return task result.

        Args:
            task (Union[str, DashScopeAPIResponse]): The task_id, or
                async_call response.
            api_key (str, optional): The api_key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The async task information.
        """
        task_id = cls._get_task_id(task)
        while True:
            rsp = cls._get(task_id, api_key)
            if rsp.status_code == HTTPStatus.OK:
                if rsp.output is None:
                    return rsp

                task_status = rsp.output['task_status']
                if task_status in [
                        TaskStatus.FAILED, TaskStatus.CANCELED,
                        TaskStatus.SUCCEEDED, TaskStatus.UNKNOWN
                ]:
                    return rsp
                else:
                    logger.info('The task %s is  %s' % (task_id, task_status))
                    time.sleep(5)
            elif rsp.status_code in REPEATABLE_STATUS:
                logger.warn(
                    ('Get task: %s temporary failure, \
                        status_code: %s, code: %s message: %s, will try again.'
                     ) % (task_id, rsp.status_code, rsp.code, rsp.message))
                time.sleep(5)
            else:
                return rsp

    @classmethod
    def async_call(cls,
                   model: str,
                   input: object,
                   task_group: str,
                   task: str = None,
                   function: str = None,
                   api_key: str = None,
                   **kwargs) -> DashScopeAPIResponse:
        """Call async service return async task information.

        Args:
            model (str): The requested model, such as gpt3-v2
            input (object): The api input data, cannot be None.
            task_group (str, optional): The api task group.
            task (str, optional): The task name. Defaults to None.
            function (str, optional): The function of the task.
                Defaults to None.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The async task information,
                which contains the task id, you can use the task id
                to query the task status.
        """
        is_stream = kwargs.pop('stream', None)  # async api not support stream.
        if is_stream:
            logger.warn('async_call do not support stream argument')
        api_key, model = BaseApi._validate_params(api_key, model)
        request = _build_api_request(model=model,
                                     input=input,
                                     task_group=task_group,
                                     task=task,
                                     function=function,
                                     api_key=api_key,
                                     async_request=True,
                                     query=False,
                                     **kwargs)
        return request.call()


class ListMixin():
    @classmethod
    async def async_list(cls,
                         api_key: str = None,
                         limits=10,
                         page=1,
                         per_page=10,
                         offset=1,
                         sortby='id',
                         order='asc',
                         **kwargs) -> DashScopeAPIResponse:
        """list objects

        Args:
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.
            limits (int, optional): Total return items. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Items per page. Defaults to 10.
            offset (int, optional): Item start position. Defaults to 1.
            sortby (str, optional): Items sort by. Defaults to 'id'.
            order (str, optional): Items order['desc', 'asc'].
                Defaults to 'desc'.

        Returns:
            DashScopeAPIResponse: The object list in output.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower())
        async with aiohttp.ClientSession() as client:
            response = await client.get(url=url,
                                        params={
                                            'limits': limits,
                                            'page': page,
                                            'per_page': per_page,
                                            'offset': offset,
                                            'sortby': sortby,
                                            'order': order,
                                        },
                                        headers={
                                            **default_headers(api_key),
                                            **headers
                                        })  # noqa E501
            return await _handle_http_response(response)


class GetMixin():
    @classmethod
    async def async_get(cls,
                        target,
                        api_key: str = None,
                        **kwargs) -> DashScopeAPIResponse:
        """Get object information.

        Args:
            target (str): The target to get, such as model_id.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The object information in output.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower(), target)
        async with aiohttp.ClientSession() as client:
            response = await client.get(url=url,
                                        headers={
                                            **default_headers(api_key),
                                            **headers
                                        })  # noqa E501
            return await _handle_http_response(response)


class DeleteMixin():
    @classmethod
    async def async_delete(cls,
                           target: str,
                           api_key: str = None,
                           **kwargs) -> DashScopeAPIResponse:
        """Get object information.

        Args:
            target (str): The object to delete, .
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The delete result.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower(), target)
        async with aiohttp.ClientSession() as client:
            response = await client.delete(url=url,
                                           headers={
                                               **default_headers(api_key),
                                               **headers
                                           })  # noqa E501
            return await _handle_http_response(response)


class CreateMixin():
    @classmethod
    async def async_call(cls,
                         json: object,
                         api_key: str = None,
                         **kwargs) -> DashScopeAPIResponse:
        """Create a object

        Args:
            json (object): The create request json body.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The created object in output.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower())
        async with aiohttp.ClientSession() as client:
            response = await client.post(url=url,
                                         json=json,
                                         headers={
                                             **default_headers(api_key),
                                             **headers
                                         })  # noqa E501
            return await _handle_http_response(response)


class UpdateMixin():
    @classmethod
    async def async_update(cls,
                           target: str,
                           json: object,
                           api_key: str = None,
                           **kwargs) -> DashScopeAPIResponse:
        """Async update a object

        Args:
            target (str): The target to update.
            json (object): The create request json body.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The updated object information in output.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower(), target)
        async with aiohttp.ClientSession() as client:
            response = await client.patch(url=url,
                                          json=json,
                                          headers={
                                              **default_headers(api_key),
                                              **headers
                                          })  # noqa E501
            return await _handle_http_response(response)


class FileUploadMixin():
    @classmethod
    async def async_upload(cls,
                           files: list,
                           descriptions: List[str] = None,
                           params: dict = None,
                           api_key: str = None,
                           **kwargs) -> DashScopeAPIResponse:
        """Upload files

        Args:
            files (list): List of (name, opened file, file_name).
            descriptions (list[str]): The file description messages.
            params (dict): The parameters
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The uploaded file information in the output.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower())
        form = aiohttp.FormData()
        for name, file, file_name in files:
            if name is None:
                form.add_field(os.path.basename(file.name),
                               file,
                               filename=file_name)
            else:
                form.add_field(name, file, filename=file_name)
        if descriptions:
            form.add_field('descriptions', json.dumps(descriptions))
        async with aiohttp.ClientSession() as client:
            response = await client.post(url=url,
                                         data=form(),
                                         params=params,
                                         headers={
                                             **default_headers(api_key),
                                             **headers
                                         })  # noqa E501
            return await _handle_http_response(response)


class CancelMixin():
    @classmethod
    async def async_cancel(cls,
                           target: str,
                           api_key: str = None,
                           **kwargs) -> DashScopeAPIResponse:
        """Cancel a job.

        Args:
            target (str): The request params, key/value map.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The cancel result.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower(), target, 'cancel')
        async with aiohttp.ClientSession() as client:
            response = await client.post(url=url,
                                         headers={
                                             **default_headers(api_key),
                                             **headers
                                         })  # noqa E501
            return await _handle_http_response(response)


class StreamEventMixin():
    @classmethod
    async def async_stream_events(cls,
                                  target,
                                  api_key: str = None,
                                  **kwargs) -> DashScopeAPIResponse:
        """Get job log.

        Args:
            target (str): The target to get, such as model_id.
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            DashScopeAPIResponse: The target outputs.
        """
        headers = kwargs.pop('headers', {})
        url = _normalization_url(cls.SUB_PATH.lower(), target, 'events')
        async with aiohttp.ClientSession() as client:
            response = await client.get(url=url,
                                        headers={
                                            **default_headers(api_key),
                                            **headers
                                        })  # noqa E501
            return await _handle_http_response(response)
