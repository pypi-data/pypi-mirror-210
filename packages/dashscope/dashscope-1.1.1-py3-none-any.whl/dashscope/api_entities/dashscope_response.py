import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, List


@dataclass(init=False)
class DictMixin(dict):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        return super().__delitem__(key)

    def get(self, key, default=None):
        return super().get(key, default)

    def setdefault(self, key, default=None):
        return super().setdefault(key, default)

    def pop(self, key, default: Any):
        return super().pop(key, default)

    def update(self, **kwargs):
        super().update(**kwargs)

    def __contains__(self, key):
        return super().__contains__(key)

    def copy(self):
        return type(self)(self)

    def getattr(self, attr):
        return super().get(attr)

    def setattr(self, attr, value):
        return super().__setitem__(attr, value)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super().__repr__())

    def __str__(self):
        return json.dumps(self, ensure_ascii=False)


@dataclass(init=False)
class DashScopeAPIResponse(DictMixin):
    """The response content

    Args:
        request_id (str): The request id.
        status_code (int): HTTP status code, 200 indicates that the
            request was successful, and others indicate an error。
        code (str): Error code if error occurs, otherwise empty str.
        message (str): Set to error message on error.
        output (Any): The request output.
        usage (Any): The request usage information.
    """
    status_code: int
    request_id: str
    code: str
    message: str
    output: Any
    usage: Any

    def __init__(self,
                 status_code: int,
                 request_id: str = '',
                 code: str = '',
                 message: str = '',
                 output: Any = None,
                 usage: Any = None,
                 **kwargs):
        super().__init__(status_code=status_code,
                         request_id=request_id,
                         code=code,
                         message=message,
                         output=output,
                         usage=usage,
                         **kwargs)


@dataclass(init=False)
class GenerationOutput(DictMixin):
    text: str

    def __init__(self, text: str, **kwargs):
        super().__init__(text=text, **kwargs)


@dataclass(init=False)
class GenerationUsage(DictMixin):
    input_tokens: int
    output_tokens: int

    def __init__(self,
                 input_tokens: int = 0,
                 output_tokens: int = 0,
                 **kwargs):
        super().__init__(input_tokens=input_tokens,
                         output_tokens=output_tokens,
                         **kwargs)


@dataclass(init=False)
class GenerationResponse(DashScopeAPIResponse):
    output: GenerationOutput
    usage: GenerationUsage

    @staticmethod
    def from_api_response(api_response: DashScopeAPIResponse):
        if api_response.status_code == HTTPStatus.OK:
            usage = {}
            if api_response.usage:
                usage = api_response.usage

            return GenerationResponse(
                status_code=api_response.status_code,
                request_id=api_response.request_id,
                code=api_response.code,
                message=api_response.message,
                output=GenerationOutput(**api_response.output),
                usage=GenerationUsage(**usage))
        else:
            return GenerationResponse(status_code=api_response.status_code,
                                      request_id=api_response.request_id,
                                      code=api_response.code,
                                      message=api_response.message)


@dataclass(init=False)
class ConversationResponse(GenerationResponse):
    pass


@dataclass(init=False)
class TranscriptionOutput(DictMixin):
    task_id: str
    task_status: str

    def __init__(self, task_id: str, task_status: str, **kwargs):
        super().__init__(task_id=task_id, task_status=task_status, **kwargs)


@dataclass(init=False)
class TranscriptionUsage(DictMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class TranscriptionResponse(DashScopeAPIResponse):
    output: TranscriptionOutput
    usage: TranscriptionUsage

    @staticmethod
    def from_api_response(api_response: DashScopeAPIResponse):
        if api_response.status_code == HTTPStatus.OK:
            output = None
            usage = None
            if api_response.output is not None:
                output = TranscriptionOutput(**api_response.output)
            if api_response.usage is not None:
                usage = TranscriptionUsage(**api_response.usage)

            return TranscriptionResponse(status_code=api_response.status_code,
                                         request_id=api_response.request_id,
                                         code=api_response.code,
                                         message=api_response.message,
                                         output=output,
                                         usage=usage)

        else:
            return TranscriptionResponse(status_code=api_response.status_code,
                                         request_id=api_response.request_id,
                                         code=api_response.code,
                                         message=api_response.message)


@dataclass(init=False)
class ImageSynthesisResult(DictMixin):
    url: str

    def __init__(self, url: str = '', **kwargs) -> None:
        super().__init__(url=url, **kwargs)


@dataclass(init=False)
class ImageSynthesisOutput(DictMixin):
    task_id: str
    task_status: str
    results: List[ImageSynthesisResult]

    def __init__(self,
                 task_id: str,
                 task_status: str,
                 results: List[ImageSynthesisResult] = [],
                 **kwargs):
        res = []
        if len(results) > 0:
            for result in results:
                res.append(ImageSynthesisResult(**result))
        super().__init__(self,
                         task_id=task_id,
                         task_status=task_status,
                         results=res,
                         **kwargs)


@dataclass(init=False)
class ImageSynthesisUsage(DictMixin):
    image_count: int

    def __init__(self, image_count: int, **kwargs):
        super().__init__(image_count=image_count, **kwargs)


@dataclass(init=False)
class ImageSynthesisResponse(DashScopeAPIResponse):
    output: ImageSynthesisOutput
    usage: ImageSynthesisUsage

    @staticmethod
    def from_api_response(api_response: DashScopeAPIResponse):
        if api_response.status_code == HTTPStatus.OK:
            output = None
            usage = None
            if api_response.output is not None:
                output = ImageSynthesisOutput(**api_response.output)
            if api_response.usage is not None:
                usage = ImageSynthesisUsage(**api_response.usage)

            return ImageSynthesisResponse(status_code=api_response.status_code,
                                          request_id=api_response.request_id,
                                          code=api_response.code,
                                          message=api_response.message,
                                          output=output,
                                          usage=usage)

        else:
            return ImageSynthesisResponse(status_code=api_response.status_code,
                                          request_id=api_response.request_id,
                                          code=api_response.code,
                                          message=api_response.message)
