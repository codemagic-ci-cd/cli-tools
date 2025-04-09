import os
from typing import AnyStr
from typing import Union


class StringConverterMixin:
    @classmethod
    def _bytes(cls, str_or_bytes: Union[str, bytes, AnyStr]) -> bytes:
        if isinstance(str_or_bytes, str):
            return str_or_bytes.encode(encoding="utf-8")
        else:
            return str_or_bytes

    @classmethod
    def _str(cls, str_or_bytes: Union[str, bytes, AnyStr]) -> str:
        if isinstance(str_or_bytes, bytes):
            return cls._bytes_to_str(str_or_bytes)
        else:
            return str_or_bytes

    @classmethod
    def _bytes_to_str(cls, bs: bytes) -> str:
        try:
            return bs.decode(encoding="utf-8")
        except UnicodeDecodeError:
            if os.name == "nt":  # Running on Windows, try Windows-1252 encoding too
                return bs.decode(encoding="windows-1252")
            raise
