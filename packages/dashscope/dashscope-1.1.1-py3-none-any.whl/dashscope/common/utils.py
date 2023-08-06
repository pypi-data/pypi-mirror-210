import asyncio
import json
import os
import platform
from http import HTTPStatus
from typing import Dict
from urllib.parse import urlparse

import aiohttp

from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.common.api_key import get_default_api_key
from dashscope.version import __version__


def is_validate_fine_tune_file(file_path):
    with open(file_path) as f:
        for line in f:
            try:
                json.loads(line)
            except json.decoder.JSONDecodeError:
                return False
    return True


def _get_task_group_and_task(module_name):
    """Get task_group and task name.
    get task_group and task name based on api file __name__

    Args:
        module_name (str): The api file __name__

    Returns:
        (str, str): task_group and task
    """
    pkg, task = module_name.rsplit('.', 1)
    task = task.replace('_', '-')
    _, task_group = pkg.rsplit('.', 1)
    return task_group, task


def is_path(path: str):
    """Check the input path is valid local path.

    Args:
        path_or_url (str): The path.

    Returns:
        bool: If path return True, otherwise False.
    """
    url_parsed = urlparse(path)
    if url_parsed.scheme in ('file', ''):
        return os.path.exists(url_parsed.path)
    else:
        return False


def is_url(url: str):
    """Check the input url is valid url.

    Args:
        url (str): The url

    Returns:
        bool: If is url return True, otherwise False.
    """
    url_parsed = urlparse(url)
    if url_parsed.scheme in ('http', 'https', 'oss'):
        return True
    else:
        return False


def iter_over_async(ait, loop):
    ait = ait.__aiter__()

    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None

    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj


def async_to_sync(async_generator):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for message in iter_over_async(async_generator, loop):
        yield message


def default_headers(api_key: str = None) -> Dict[str, str]:
    ua = 'dashscope/%s; python/%s; platform/%s; processor/%s' % (
        __version__,
        platform.python_version(),
        platform.platform(),
        platform.processor(),
    )
    headers = {'user-agent': ua}
    if api_key is None:
        api_key = get_default_api_key()
    headers['Authorization'] = 'Bearer %s' % api_key
    headers['Accept'] = 'application/json'
    return headers


async def _handle_http_response(response: aiohttp.ClientResponse):
    request_id = ''
    if response.status == HTTPStatus.OK:
        json_content = await response.json()
        if 'request_id' in json_content:
            request_id = json_content['request_id']
        return DashScopeAPIResponse(request_id=request_id,
                                    status_code=HTTPStatus.OK,
                                    output=json_content)
    else:
        if 'application/json' in response.content_type:
            error = await response.json()
            msg = ''
            if 'message' in error:
                msg = error['message']
            if 'request_id' in error:
                request_id = error['request_id']
            return DashScopeAPIResponse(request_id=request_id,
                                        status_code=response.status,
                                        output=None,
                                        code=error['code'],
                                        message=msg)
        else:
            msg = await response.read()
            return DashScopeAPIResponse(request_id=request_id,
                                        status_code=response.status,
                                        output=None,
                                        code='Unknown',
                                        message=msg)
