import json
from abc import abstractmethod
from typing import Dict

_json_encoder_default = json.JSONEncoder.default


class JsonSerializableMeta(type):
    @staticmethod
    def default(json_encoder, obj) -> Dict:
        if isinstance(obj, JsonSerializable):
            return obj.dict()
        else:
            return _json_encoder_default(json_encoder, obj)

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        json.JSONEncoder.default = JsonSerializableMeta.default


class JsonSerializable(metaclass=JsonSerializableMeta):
    @abstractmethod
    def dict(self) -> Dict:
        raise NotImplementedError(f"Method {self.__class__.__name__}.{self.dict.__name__} is not implemented")

    def json(self, *args, indent=4, **kwargs) -> str:
        if "indent" not in kwargs:
            kwargs["indent"] = indent
        return json.dumps(self, *args, **kwargs)
