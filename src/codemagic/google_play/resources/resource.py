from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from codemagic.models import JsonSerializable
from codemagic.models import JsonSerializableMeta


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


class PrettyNameMeta(JsonSerializableMeta):
    def __str__(cls):  # noqa: N805
        class_name = cls.__name__
        name = re.sub(r'([A-Z])', r' \1', class_name).lstrip(' ')
        return re.sub('Id', 'ID', name)

    @property
    def s(cls) -> str:  # noqa: N805
        """ Plural name of the object """
        return cls.plural()

    def plural(cls, count: Optional[int] = None) -> str:  # noqa: N805
        """ Optional plural name of the object depending on the count """
        singular = str(cls)
        if count == 1:
            return singular
        if singular.endswith('y'):
            return f'{singular[:-1]}ies'
        return f'{singular}s'


@dataclass
class Resource(DictSerializable, JsonSerializable, metaclass=PrettyNameMeta):
    def _format_attribute_name(self, name: str) -> str:
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.lower().capitalize()

    def _format_attribute_value(self, value: Any) -> Any:
        if isinstance(value, enum.Enum):
            return value.value
        if isinstance(value, DictSerializable):
            lines = '\n'.join(
                f'\t{self._format_attribute_name(k)}: {v}' for k, v in value.dict().items())
            return f'\n{lines}'
        return value

    def __str__(self) -> str:
        s = super().__str__()
        for attribute_name, value in self.__dict__.items():
            if value is None:
                continue
            name = self._format_attribute_name(attribute_name)
            value = self._format_attribute_value(value)
            s += f'\n{name}: {value}'
        return s
