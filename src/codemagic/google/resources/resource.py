from __future__ import annotations

import enum
import re
from typing import Any
from typing import Tuple

from codemagic.models import DictSerializable
from codemagic.models import JsonSerializable


class Resource(DictSerializable, JsonSerializable):
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
