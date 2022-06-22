from typing import AnyStr
from typing import Union


class StringConverterMixin:

    @classmethod
    def _bytes(cls, str_or_bytes: Union[str, bytes, AnyStr]) -> bytes:
        if isinstance(str_or_bytes, str):
            return str_or_bytes.encode(encoding='utf-8')
        else:
            return str_or_bytes

    @classmethod
    def _str(cls, str_or_bytes: Union[str, bytes, AnyStr]) -> str:
        if isinstance(str_or_bytes, bytes):
            return str_or_bytes.decode(encoding='utf-8')
        else:
            return str_or_bytes
