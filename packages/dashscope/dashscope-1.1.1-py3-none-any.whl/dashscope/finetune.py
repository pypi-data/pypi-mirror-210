import asyncio
from typing import Union

from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.client.base_api import (CancelMixin, CreateMixin, DeleteMixin,
                                       GetMixin, ListMixin, StreamEventMixin)


class FineTune(CreateMixin, CancelMixin, DeleteMixin, ListMixin, GetMixin,
               StreamEventMixin):
    SUB_PATH = 'fine-tunes'

    @classmethod
    def call(cls,
             model: str,
             training_file_ids: Union[list, str],
             validation_file_ids: Union[list, str] = None,
             hyper_parameters: dict = {},
             api_key: str = None,
             **kwargs) -> DashScopeAPIResponse:
        """Create fine-tune job

        Args:
            model (str): The model to be fine-tuned
            training_file_ids (list, str): Ids of the fine-tune training data,
                which can be pre-uploaded using the File API.
            validation_file_ids ([list,str], optional): Ids of the fine-tune
                validating data, which can be pre-uploaded using the File API.
            hyper_parameters (dict, optional): The fine-tune hyper parameters.
                Defaults to empty.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The request result.
        """
        request = {
            'model': model,
            'training_file_ids': training_file_ids,
            'validation_file_ids': validation_file_ids,
            'hyper_parameters': hyper_parameters if hyper_parameters else {},
        }
        return asyncio.run(super().async_call(request, api_key, **kwargs))

    @classmethod
    def cancel(cls,
               job_id: str,
               api_key: str = None,
               **kwargs) -> DashScopeAPIResponse:
        """Cancel a running fine-tune job.

        Args:
            job_id (str): The fine-tune job id.
            api_key (str, optional): The api api_key, can be None,
                if None, will get by default rule(TODO: api key doc).

        Returns:
            DashScopeAPIResponse: The request result.
        """
        return asyncio.run(super().async_cancel(job_id, api_key, **kwargs))

    @classmethod
    def list(cls,
             api_key: str = None,
             limits=10,
             page=1,
             per_page=10,
             offset=1,
             sortby='id',
             order='asc',
             **kwargs) -> DashScopeAPIResponse:
        """List fine-tune job.

        Args:
            api_key (str, optional): The api key
            limits (int, optional): Total return items. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Items per page. Defaults to 10.
            offset (int, optional): Item start position. Defaults to 1.
            sortby (str, optional): Items sort by. Defaults to 'id'.
            order (str, optional): Items order['desc', 'asc'].
                Defaults to 'asc'.

        Returns:
            DashScopeAPIResponse: The fine-tune jobs in the result.
        """
        return asyncio.run(super().async_list(api_key, limits, page, per_page,
                                              offset, sortby, order, **kwargs))

    @classmethod
    def get(cls,
            job_id: str,
            api_key: str = None,
            **kwargs) -> DashScopeAPIResponse:
        """Get fine-tune job information.

        Args:
            job_id (str): The fine-tune job id
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The job info
        """
        return asyncio.run(super().async_get(job_id, api_key, **kwargs))

    @classmethod
    def delete(cls,
               job_id: str,
               api_key: str = None,
               **kwargs) -> DashScopeAPIResponse:
        """Delete a fine-tune job.

        Args:
            job_id (str): The fine-tune job id.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The delete result.
        """
        return asyncio.run(super().async_delete(job_id, api_key, **kwargs))

    @classmethod
    def stream_events(cls,
                      job_id: str,
                      api_key: str = None,
                      **kwargs) -> DashScopeAPIResponse:
        """Get fine-tune job events.

        Args:
            job_id (str): The fine-tune job id
            api_key (str, optional): the api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The job log events.
        """
        return asyncio.run(super().async_stream_events(job_id, api_key,
                                                       **kwargs))
