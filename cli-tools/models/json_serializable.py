import json
from abc import abstractmethod
from typing import Dict


class _JsonSerializableType(type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        json.JSONEncoder.default = lambda _, cls_instance: cls_instance.dict()


class JsonSerializable(metaclass=_JsonSerializableType):

    @abstractmethod
    def dict(self) -> Dict:
        raise NotImplementedError
