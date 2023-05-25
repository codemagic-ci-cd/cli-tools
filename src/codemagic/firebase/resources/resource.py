from __future__ import annotations

from abc import ABC
from typing import ClassVar
from typing import Optional
from typing import TypeVar

ResourceT = TypeVar('ResourceT', bound='Resource')


class Resource(ABC):
    __google_api_label__: ClassVar[Optional[str]] = None

    @classmethod
    def get_label(cls) -> str:
        if cls.__google_api_label__:
            return cls.__google_api_label__
        return f'{cls.__name__.lower()}s'
