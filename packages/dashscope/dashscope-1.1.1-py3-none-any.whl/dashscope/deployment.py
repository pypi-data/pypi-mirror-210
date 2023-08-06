import asyncio
from typing import Any

from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.client.base_api import (CreateMixin, DeleteMixin, GetMixin,
                                       ListMixin, StreamEventMixin)


class Deployment(CreateMixin, DeleteMixin, ListMixin, GetMixin,
                 StreamEventMixin):
    SUB_PATH = 'deployments'
    """Deploy a model.
    """
    @classmethod
    def call(cls,
             model: str,
             scale: Any = None,
             suffix: str = None,
             api_key: str = None,
             **kwargs) -> DashScopeAPIResponse:
        """Deploy a model service.

        Args:
            model (str): The model id.
            scale (Any): Currently not supported.
            suffix (str, optional): The name suffix of the deployment,
               default: model_a_b_c, with suffix will be:
               model_suffix.
            api_key (str, optional): The api api_key, can be None,
                if None, will get by default rule(TODO: api key doc).

        Returns:
            DashScopeAPIResponse: The request result.
        """
        req = {'model': model, 'suffix': suffix}
        return asyncio.run(super().async_call(req, api_key, **kwargs))

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
        """List deployments.

        Args:
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.
            limits (int, optional): Total return items. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Items per page. Defaults to 10.
            offset (int, optional): Item start position. Defaults to 1.
            sortby (str, optional): Items sort by. Defaults to 'id'.
            order (str, optional): Items order['desc', 'asc'].
                Defaults to 'asc'.

        Returns:
            DashScopeAPIResponse: The deployment list.
        """
        return asyncio.run(super().async_list(api_key, limits, per_page,
                                              offset, sortby, order, **kwargs))

    @classmethod
    def get(cls,
            deployment_id: str,
            api_key: str = None,
            **kwargs) -> DashScopeAPIResponse:
        """Get model deployment information.

        Args:
            deployment_id (str): The deployment_id.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The deployment information.
        """
        return asyncio.run(super().async_get(deployment_id, api_key, **kwargs))

    @classmethod
    def delete(cls,
               deployment_id: str,
               api_key: str = None,
               **kwargs) -> DashScopeAPIResponse:
        """Delete model deployment.

        Args:
            deployment_id (str): The deployment id.
            api_key (str, optional): The api key. Defaults to None.

        Returns:
            DashScopeAPIResponse: The delete result.
        """
        return asyncio.run(super().async_delete(deployment_id, api_key,
                                                **kwargs))
