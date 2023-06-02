from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

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
    def _format_dict_attribute_value(cls, value: Union[DictSerializable, dict], tabs_count: int) -> str:
        if isinstance(value, DictSerializable):
            value = value.dict()

        indentation = '\t' * tabs_count

        if isinstance(value, (DictSerializable, dict, list)):
            new_tabs_count = tabs_count  # Do not use extra indentation
        else:
            new_tabs_count = tabs_count + 1

        return ''.join([
            f'\n{indentation}'
            f'{cls._format_attribute_name(k)}: '
            f'{cls._format_attribute_value(v, new_tabs_count)}'
            for k, v in value.items()
        ])

    @classmethod
    def _format_list_attribute_value(cls, value: list, tabs_count: int) -> str:
        indentation = '\t' * (tabs_count + 1)
        previous_indentation = '\t' * tabs_count
        items: List[str] = []

        for item in value:
            formatted_item = cls._format_attribute_value(item, tabs_count + 1)
            if isinstance(item, (DictSerializable, dict, list)):
                items.append(formatted_item)
            else:
                items.append(f'\n{indentation}{formatted_item}')

        str_items = '\n'.join(items)
        return f'[{str_items}\n{previous_indentation}]'

    @classmethod
    def _format_attribute_value(cls, value: Any, tabs_count: int = 0) -> str:
        if isinstance(value, (DictSerializable, dict)):
            return cls._format_dict_attribute_value(value, tabs_count)
        elif isinstance(value, list):
            return cls._format_list_attribute_value(value, tabs_count)
        elif isinstance(value, enum.Enum):
            return str(value.value)
        else:
            return str(value)

    def __str__(self) -> str:
        return ''.join([
            f'\n{self._format_attribute_name(k)}: {self._format_attribute_value(v)}'
            for k, v in self.__dict__.items() if v is not None
        ])
