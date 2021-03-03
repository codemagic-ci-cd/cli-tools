from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Tuple

from codemagic.models import JsonSerializable


class DictSerializable:
    _OMIT_KEYS: Tuple[str, ...] = ('_raw',)
    _OMIT_IF_NONE_KEYS: Tuple[str, ...] = tuple()

    @classmethod
    def _serialize(cls, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, DictSerializable):
            return obj.dict()
        if isinstance(obj, (list, tuple)):
            return [cls._serialize(item) for item in obj]
        return obj

    @classmethod
    def _should_omit(cls, key, value) -> bool:
        if key.startswith('_'):
            return True
        if key in cls._OMIT_KEYS:
            return True
        if key in cls._OMIT_IF_NONE_KEYS and value is None:
            return True
        return False

    def dict(self) -> Dict:
        return {k: self._serialize(v) for k, v in self.__dict__.items() if not self._should_omit(k, v)}


@dataclass
class Resource(DictSerializable, JsonSerializable):
    @classmethod
    def _format_attribute_name(cls, name: str) -> str:
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.lower().capitalize()

    @classmethod
    def _format_attribute_value(cls, value: Any, tabs_count: int = 0) -> Any:
        def _no_extra_identation(value: Any) -> bool:
            return isinstance(value, (DictSerializable, dict, list))

        if isinstance(value, (DictSerializable, dict)):
            if isinstance(value, DictSerializable):
                value = value.dict()
            identation = '\t' * tabs_count
            new_tabs_count = tabs_count if _no_extra_identation(value) else tabs_count + 1
            return ''.join([
                f'\n{identation}'
                f'{cls._format_attribute_name(k)}: '
                f'{cls._format_attribute_value(v, new_tabs_count)}'
                for k, v in value.items()
            ])
        if isinstance(value, list):
            identation = '\t' * (tabs_count + 1)
            previous_identation = '\t' * tabs_count
            items = []
            for item in value:
                formatted_item = cls._format_attribute_value(item, tabs_count + 1)
                prefix = '' if _no_extra_identation(item) else f'\n{identation}'
                items.append(f'{prefix}{formatted_item}')
            str_items = '\n'.join(items)
            return f'[{str_items}\n{previous_identation}]'
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def __str__(self) -> str:
        return ''.join([
            f'\n{self._format_attribute_name(k)}: {self._format_attribute_value(v)}'
            for k, v in self.__dict__.items() if v is not None
        ])
