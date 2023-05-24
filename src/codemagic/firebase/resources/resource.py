from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from typing import Dict


class DictSerializable:
    @classmethod
    def _serialize(cls, obj):
        if isinstance(obj, DictSerializable):
            return obj.dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    def dict(self) -> Dict:
        return {k: self._serialize(v) for k, v in self.__dict__.items()}


@dataclass
class Resource(DictSerializable, ABC):
    label: ClassVar[str]
