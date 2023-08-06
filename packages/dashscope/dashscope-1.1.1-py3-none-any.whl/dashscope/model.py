import asyncio

from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.client.base_api import GetMixin, ListMixin


class Model(ListMixin, GetMixin):
    SUB_PATH = 'models'

    @classmethod
    def get(cls,
            name: str,
            api_key: str = None,
            **kwargs) -> DashScopeAPIResponse:
        """Get the model information.

        Args:
            name (str): The model name.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The model information.
        """
        return asyncio.run(super().async_get(name, api_key, **kwargs))

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
        """List models.

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
            DashScopeAPIResponse: The models.
        """
        return asyncio.run(super().async_list(api_key, limits, page, per_page,
                                              offset, sortby, order, **kwargs))
