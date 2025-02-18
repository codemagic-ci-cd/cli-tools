import enum
from datetime import datetime
from typing import Tuple


class DictSerializable:
    _OMIT_KEYS: Tuple[str, ...] = ("_raw",)
    _OMIT_IF_NONE_KEYS: Tuple[str, ...] = tuple()

    @classmethod
    def _serialize(cls, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, DictSerializable):
            return obj.dict()
        if isinstance(obj, (list, tuple)):
            return [cls._serialize(item) for item in obj]
        return obj

    @classmethod
    def _should_omit(cls, key, value) -> bool:
        if key.startswith("_"):
            return True
        if key in cls._OMIT_KEYS:
            return True
        if key in cls._OMIT_IF_NONE_KEYS and value is None:
            return True
        return False

    def dict(self) -> dict:
        return {k: self._serialize(v) for k, v in self.__dict__.items() if not self._should_omit(k, v)}
