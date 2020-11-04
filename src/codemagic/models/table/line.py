from typing import Any
from typing import Optional

from codemagic.cli import Colors


class Line:
    def __init__(self,
                 key: str,
                 value: Any,
                 key_color: Optional[Colors] = None,
                 value_color: Optional[Colors] = None):
        self._key = key
        self._value = value
        self._key_color = key_color
        self._value_color = value_color

    def is_content_line(self) -> bool:
        return self.__class__ is Line

    @property
    def key_length(self) -> int:
        return len(str(self._key))

    @property
    def value_length(self) -> int:
        return len(str(self._value))

    @classmethod
    def _get_formatted(cls, item: Any, width: int, color: Optional[Colors], align_left: bool) -> str:
        if align_left:
            s = str(item).ljust(width)
        else:
            s = str(item).rjust(width)
        return color(s) if color else s

    def get_key(self, width: int, align_left: bool = True) -> str:
        return self._get_formatted(self._key, width, self._key_color, align_left)

    def get_value(self, width: int, align_left: bool = True) -> str:
        return self._get_formatted(self._value, width, self._value_color, align_left)


class Spacer(Line):
    def __init__(self):
        super().__init__('', '')


class Header(Line):
    def __init__(self, header: str):
        super().__init__(header, '')

    def get_header(self) -> str:
        return str(self._key)
