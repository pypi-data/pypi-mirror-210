import asyncio

from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.client.base_api import (DeleteMixin, FileUploadMixin, GetMixin,
                                       ListMixin)
from dashscope.common.constants import FilePurpose
from dashscope.common.error import InvalidFileFormat
from dashscope.common.utils import is_validate_fine_tune_file


class File(FileUploadMixin, ListMixin, DeleteMixin, GetMixin):
    SUB_PATH = 'files'

    @classmethod
    def upload(cls,
               file_path: str,
               purpose: str = FilePurpose.fine_tune,
               description: str = None,
               api_key: str = None,
               **kwargs) -> DashScopeAPIResponse:
        """Upload file for model fine-tune or other tasks.

        Args:
            file_path (str): The local file name to upload.
            purpose (str): The purpose of the file[fine-tune|inference]
            description (str, optional): The file description message.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The upload information
        """
        if purpose == FilePurpose.fine_tune:
            if not is_validate_fine_tune_file(file_path):
                raise InvalidFileFormat(
                    'The file %s is not in valid jsonl format' % file_path)
        with open(file_path, 'rb') as f:
            return asyncio.run(super().async_upload(
                files=[('files', f, None)],
                descriptions=[description]
                if description is not None else None,
                api_key=api_key,
                **kwargs))

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
        """List uploaded files.

        Args:
            api_key (str, optional):
            The api api_key, can be None,
                if None, will get by default rule(TODO: api key doc).
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
            file_id: str,
            api_key: str = None,
            **kwargs) -> DashScopeAPIResponse:
        """Get the file info.

        Args:
            file_id (str): The file id.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The job info
        """
        return asyncio.run(super().async_get(file_id, api_key, **kwargs))

    @classmethod
    def delete(cls,
               file_id: str,
               api_key: str = None,
               **kwargs) -> DashScopeAPIResponse:
        """Delete uploaded file.

        Args:
            file_id (str): The file id want to delete.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: Delete result.
        """
        return asyncio.run(super().async_delete(file_id, api_key, **kwargs))
