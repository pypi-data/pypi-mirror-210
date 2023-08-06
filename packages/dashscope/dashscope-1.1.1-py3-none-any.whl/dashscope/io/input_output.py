import base64
import io
from typing import Generator

from dashscope.common.error import UnsupportedDataType


class InputResolver:
    def __init__(self,
                 input_instance,
                 is_encode_binary: bool = True,
                 custom_type_resolver: dict = {}):
        self._instance = input_instance
        self._is_encode_binary = is_encode_binary
        self._custom_type_resolver = custom_type_resolver

    def __next__(self):
        while True:
            return resolve_input(self._instance, self._is_encode_binary,
                                 self._custom_type_resolver)

    def __iter__(self):
        return self


def resolve_input(input, is_encode_binary, custom_type_resolver: dict = {}):
    """Resolve input data, if same field is file, generator, we can get data.

    Args:
        input (object): object
        is_encode_binary (bool): is encode binary, websocket support binary,
            no need encode.
        custom_type_resolver (map): key: the data type, value,
            the data convert, which convert data type key, to jsonable object.
            def ndarray_tolist(ndar):
                return ndar.tolist()
            {numpy.ndarray: ndarray_tolist}

    Raises:
        UnsupportedDataType: Unsupported data type

    Returns:
        object: The jsonable object.
    """
    if input is None:
        return None
    if isinstance(input, dict):
        out_input = {}
        for key, value in input.items():
            out_input[key] = resolve_input(value, is_encode_binary,
                                           custom_type_resolver)
        return out_input
    elif isinstance(input, (list, tuple, set)):
        out_input = []
        for item in input:
            out_input.append(
                resolve_input(item, is_encode_binary, custom_type_resolver))
        return out_input
    elif isinstance(input, str):
        return input
    elif isinstance(input, (int, float, complex)):
        return input
    elif isinstance(input, bool):
        return input
    elif isinstance(input, (bytearray, bytes, memoryview)):
        if is_encode_binary:
            return base64.b64encode(input).decode('ascii')
        else:
            return input
    elif isinstance(input, io.IOBase):
        content = input.read()
        if not content:
            raise StopIteration  # read file end.
        return content
    elif isinstance(input, Generator):
        output = next(input)
        return resolve_input(output, is_encode_binary, custom_type_resolver)
    elif type(input) in custom_type_resolver:
        return custom_type_resolver[type(input)](input)
    else:
        raise UnsupportedDataType('Unsupported atom data type: %s' %
                                  type(input))
