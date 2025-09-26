from __future__ import annotations

import dataclasses
import enum
import re
from abc import ABCMeta
from typing import TYPE_CHECKING

from codemagic.models import DictSerializable
from codemagic.models import JsonSerializable
from codemagic.models import JsonSerializableMeta
from codemagic.utilities import log

if TYPE_CHECKING:
    from typing import Any
    from typing import Dict
    from typing import Mapping
    from typing import Tuple
    from typing import Type
    from typing import TypeVar

    R = TypeVar("R", bound="Resource")


class ResourceAbcMeta(JsonSerializableMeta, ABCMeta):
    pass


@dataclasses.dataclass
class Resource(DictSerializable, JsonSerializable, metaclass=ResourceAbcMeta):
    @classmethod
    def _get_defined_fields(cls, given_fields: Mapping[str, Any]) -> Dict[str, Any]:
        logger = log.get_logger(cls, log_to_stream=False)
        defined_fields = {f.name for f in dataclasses.fields(cls)}
        fields = {}
        for field_name, field_value in given_fields.items():
            if field_name in defined_fields:
                fields[field_name] = field_value
            else:
                logger.warning("Unknown field %r for resource %s", field_name, cls.__name__)
        return fields

    @classmethod
    def from_api_response(cls: Type[R], api_response: Mapping[str, Any]) -> R:
        defined_fields = cls._get_defined_fields(api_response)
        return cls(**defined_fields)

    @staticmethod
    def _format_attribute_name(name: str) -> str:
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        name = name.lower().capitalize()
        return re.sub(r"uri", "URI", name, flags=re.IGNORECASE)

    @classmethod
    def _format_dict_attribute_value(cls, value: DictSerializable | dict) -> Tuple[str, bool]:
        if isinstance(value, DictSerializable):
            value = value.dict()

        lines = []
        for k, v in value.items():
            if v is None:
                continue

            formatted_name = cls._format_attribute_name(k)
            formatted_value, indent = cls._format_attribute_value(v)

            if indent:
                lines.append(f"{formatted_name}:")
                for line in formatted_value.splitlines(keepends=False):
                    lines.append(f"    {line}")
            else:
                lines.append(f"{formatted_name}: {formatted_value}")
        return "\n".join(lines), True

    @classmethod
    def _format_list_attribute_value(cls, value: list) -> Tuple[str, bool]:
        lines = []
        for item in value:
            formatted_item, _ = cls._format_attribute_value(item)
            for i, line in enumerate(formatted_item.splitlines(keepends=False)):
                lines.append(f"{'-' if i == 0 else ' '} {line}")
        return "\n".join(lines), True

    @classmethod
    def _format_attribute_value(cls, attribute_value: Any) -> Tuple[str, bool]:
        if isinstance(attribute_value, (DictSerializable, dict)):
            return cls._format_dict_attribute_value(attribute_value)
        elif isinstance(attribute_value, list):
            return cls._format_list_attribute_value(attribute_value)
        elif isinstance(attribute_value, enum.Enum):
            return str(attribute_value.value), False
        return str(attribute_value), False

    def __str__(self) -> str:
        formatted_value, _ = self._format_attribute_value(self)
        return formatted_value
