import asyncio
import os
import time
from http import HTTPStatus
from typing import List, Union
from urllib.parse import urlparse

import aiohttp

from dashscope.api_entities.dashscope_response import (AsyncTaskResponse,
                                                       DashScopeAPIResponse)
from dashscope.client.base_api import BaseAsyncApi
from dashscope.common.constants import ApiProtocol, HTTPMethod
from dashscope.common.logging import logger
from dashscope.common.utils import _get_task_group_and_task


class Transcribe(BaseAsyncApi):
    """API for File Transcription models.
    """

    MAX_QUERY_TRY_COUNT = 3

    class Models:
        paraformer_v1 = 'paraformer-v1'
        paraformer_8k_v1 = 'paraformer-8k-v1'
        paraformer_mtl_v1 = 'paraformer-mtl-v1'

    @classmethod
    def call(cls, model: str, file_urls: List[str],
             **kwargs) -> DashScopeAPIResponse:
        """Transcribe the given files synchronously.

        Args:
            model (str): The requested model_id.
            file_urls (List[str]): List of stored URLs.
            channel_id (List[int], optional): The selected channel_id of audio file. # noqa: E501

        Returns:
            DashScopeAPIResponse: The result of batch transcription.
        """
        return super().call(model, file_urls, **kwargs)

    @classmethod
    def async_call(cls, model: str, file_urls: List[str],
                   **kwargs) -> AsyncTaskResponse:
        """Transcribe the given files asynchronously,
        return the status of task submission for querying results subsequently.

        Args:
            model (str): The requested model, such as paraformer-16k-1
            file_urls (List[str]): List of stored URLs.
            channel_id (List[int], optional): The selected channel_id of audio file. # noqa: E501

        Returns:
            AsyncTaskResponse: The response including task_id.
        """
        cls.files, cls.error_msg = cls._validate_files(file_urls)
        cls.model_id = model

        if cls.error_msg is not None:
            logger.error(cls.error_msg)
            return AsyncTaskResponse(request_id='',
                                     code=HTTPStatus.BAD_REQUEST,
                                     output=None,
                                     message=cls.error_msg)

        # launch transcribe request, and get task info.
        response = cls._launch_request(cls.files, **kwargs)

        return response

    @classmethod
    def fetch(cls, task: Union[str,
                               DashScopeAPIResponse]) -> DashScopeAPIResponse:
        """Fetch the status of task, including results of batch transcription when status is SUCCEEDED.  # noqa: E501

        Args:
            task (Union[str, DashScopeAPIResponse]): The task_id or
                response including task_id returned from async_call().

        Returns:
            DashScopeAPIResponse: The status of task_id,
        including results of batch transcription when status is SUCCEEDED.
        """
        response = DashScopeAPIResponse(request_id='',
                                        code=HTTPStatus.OK,
                                        output=None)

        try_count: int = 0
        while True:
            try:
                response = super().fetch(task)
            except (asyncio.TimeoutError, aiohttp.ClientConnectorError) as e:
                logger.error(e)
                try_count += 1
                if try_count <= Transcribe.MAX_QUERY_TRY_COUNT:
                    time.sleep(2)
                    continue
            except Exception as e:
                logger.error(e)
                break

            try_count = 0
            break

        return response

    @classmethod
    def wait(cls, task: Union[str,
                              DashScopeAPIResponse]) -> DashScopeAPIResponse:
        """Poll task until the final results of transcription is obtained.

        Args:
            task (Union[str, DashScopeAPIResponse]): The task_id or
                response including task_id returned from async_call().

        Returns:
            DashScopeAPIResponse: The result of batch transcription.
        """
        return super().wait(task)

    @classmethod
    def _launch_request(cls, files: List[str], **kwargs) -> AsyncTaskResponse:
        """Submit transcribe request.

        Args:
            files (List[str]): List of stored URLs.

        Returns:
            AsyncTaskResponse: The result of task submission.
        """
        response = AsyncTaskResponse(request_id='', code=HTTPStatus.OK)

        task_name, function = _get_task_group_and_task(__name__)

        try_count: int = 0
        while True:
            try:
                response = super().async_call(model=cls.model_id,
                                              task_group='audio',
                                              task=task_name,
                                              function=function,
                                              input={'file_urls': files},
                                              api_protocol=ApiProtocol.HTTP,
                                              http_method=HTTPMethod.POST,
                                              **kwargs)
            except (asyncio.TimeoutError, aiohttp.ClientConnectorError) as e:
                logger.error(e)
                try_count += 1
                if try_count <= Transcribe.MAX_QUERY_TRY_COUNT:
                    time.sleep(2)
                    continue
            except Exception as e:
                logger.error(e)
                break

            break

        return response

    @classmethod
    def _validate_files(cls, files: List[str]):
        """Check the validity of the file and whether the file is a URL.

        Args:
            files (List[str]): List of stored URLs.

        Returns:
            files (List[str]): List of stored URLs.
            error_msg (str): Error message.
        """
        error_msg = None
        if files is None or len(files) == 0:
            error_msg = 'No file has been passed in, please confirm to input valid files!'  # noqa: E501
            return files, error_msg

        for file in files:
            if os.path.isfile(file):
                error_msg = 'Input an illegal local file, please ensure that the file type is URL!'  # noqa: E501
            else:
                result = urlparse(file)
                if result.scheme is not None and len(result.scheme) > 0:
                    if result.scheme != 'http' and result.scheme != 'https':
                        error_msg = f'The URL protocol({result.scheme}) of file({file}) is not http or https.'  # noqa: E501
                        break
                else:
                    error_msg = f'Input an illegal file({file}), maybe the file is inexistent.'  # noqa: E501
                    break

        return files, error_msg
