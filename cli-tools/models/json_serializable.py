import json
from abc import abstractmethod
from typing import Dict

_json_encoder_default = json.JSONEncoder.default


class _JsonSerializableMeta(type):

    @staticmethod
    def default(json_encoder, obj):
        if isinstance(obj, JsonSerializable):
            return obj.dict()
        else:
            return _json_encoder_default(json_encoder, obj)

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        json.JSONEncoder.default = _JsonSerializableMeta.default


class JsonSerializable(metaclass=_JsonSerializableMeta):

    @abstractmethod
    def dict(self) -> Dict:
        raise NotImplementedError(f'Method {self.__class__.__name__}.{self.dict.__name__} is not implemented')

    def json(self):
        return json.dumps(self)
