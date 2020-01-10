from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from typing import overload

from codemagic.models import JsonSerializable
from codemagic.models import JsonSerializableMeta
from .enums import ResourceType


class ResourceId(str):
    pass


class DictSerializable:
    _OMIT_KEYS: Tuple[str, ...] = ('_raw',)
    _OMIT_IF_NONE_KEYS: Tuple[str, ...] = tuple()

    @classmethod
    def _serialize(cls, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return Resource.to_iso_8601(obj)
        elif isinstance(obj, DictSerializable):
            return obj.dict()
        elif isinstance(obj, (list, tuple)):
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
class PagingInformation(DictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/paginginformation
    """

    @dataclass
    class Paging(DictSerializable):
        total: int
        limit: int

    paging: Paging

    def __post_init__(self):
        if isinstance(self.paging, dict):
            self.paging = PagingInformation.Paging(**self.paging)


class Links(DictSerializable):
    _OMIT_IF_NONE_KEYS = ('related',)

    def __init__(_self, self: str, related: Optional[str] = None):
        _self.self = self
        _self.related = related


class ResourceLinks(DictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/resourcelinks
    """

    def __init__(_self, self):
        _self.self = self


@dataclass
class Data(DictSerializable):
    id: str
    type: ResourceType

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = ResourceType(self.type)


@dataclass
class Relationship(DictSerializable):
    _OMIT_IF_NONE_KEYS = ('data', 'meta')

    links: Links
    data: Optional[Union[Data, List[Data]]] = None
    meta: Optional[PagingInformation] = None

    def __post_init__(self):
        if isinstance(self.links, dict):
            self.links = Links(**self.links)
        if isinstance(self.data, dict):
            self.data = Data(**self.data)
        elif isinstance(self.data, list):
            if self.data and isinstance(self.data[0], dict):
                self.data = [Data(**data) for data in self.data]
        if isinstance(self.meta, dict):
            self.meta = PagingInformation(**self.meta)


class LinkedResourceData(DictSerializable, JsonSerializable):

    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.type = ResourceType(api_response['type'])
        self.id: ResourceId = ResourceId(api_response['id'])

    def __str__(self):
        return '\n'.join([
            f'Id: {self.id}',
            f'Type: {self.type.value}'
        ])


class PrettyNameMeta(JsonSerializableMeta):
    def __str__(cls):
        class_name = cls.__name__
        name = re.sub(f'([A-Z])', r' \1', class_name).lstrip(' ')
        return re.sub('Id', 'ID', name)

    @property
    def s(cls) -> str:
        """ Plural name of the object """
        return cls.plural()

    def plural(cls, count: Optional[int] = None) -> str:
        """ Optional plural name of the object depending on the count """
        singular = str(cls)
        if count == 1:
            return singular
        if singular.endswith('y'):
            return f'{singular[:-1]}ies'
        return f'{singular}s'


class Resource(LinkedResourceData, metaclass=PrettyNameMeta):
    @dataclass
    class Attributes(DictSerializable):
        def __init__(self, *args, **kwargs):
            pass

    @dataclass
    class Relationships(DictSerializable):
        def __init__(self, *args, **kwargs):
            pass

        def __post_init__(self):
            for field in self.__dict__:
                value = getattr(self, field)
                if not isinstance(value, Relationship):
                    setattr(self, field, Relationship(**value))

    @classmethod
    def _create_attributes(cls, api_response):
        return cls.Attributes(**api_response['attributes'])

    @classmethod
    def _create_relationships(cls, api_response):
        return cls.Relationships(**api_response['relationships'])

    def __init__(self, api_response: Dict, created: bool = False):
        super().__init__(api_response)
        self._created = created
        self.links: ResourceLinks = ResourceLinks(**api_response['links'])
        self.attributes = self._create_attributes(api_response)
        if 'relationships' in api_response:
            self.relationships = self._create_relationships(api_response)

    @property
    def created(self) -> bool:
        return self._created

    @classmethod
    @overload
    def from_iso_8601(cls, iso_8601_timestamp: None) -> None:
        ...

    @classmethod
    @overload
    def from_iso_8601(cls, iso_8601_timestamp: str) -> datetime:
        ...

    @classmethod
    def from_iso_8601(cls, iso_8601_timestamp: Optional[str]):
        if iso_8601_timestamp is None:
            return None
        return datetime.strptime(iso_8601_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')

    @classmethod
    @overload
    def to_iso_8601(cls, dt: None) -> None:
        ...

    @classmethod
    @overload
    def to_iso_8601(cls, dt: datetime) -> str:
        ...

    @classmethod
    def to_iso_8601(cls, dt: Optional[datetime]):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+0000'

    def _format_attribute_name(self, name: str) -> str:
        type_prefix = self.type.value.rstrip('s')
        name = re.sub(f'{type_prefix}s?', '', name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.lower().capitalize()

    def _hide_attribute_value(self, attribute_name: str) -> bool:
        if not hasattr(self.attributes, '__dataclass_fields__'):
            return False
        field = self.attributes.__dataclass_fields__[attribute_name]
        return field.metadata.get('hide') is True

    def _format_attribute_value(self, attribute_name: str, value: Any) -> Any:
        if self._hide_attribute_value(attribute_name):
            return '"..."'
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def __str__(self) -> str:
        s = super().__str__()
        for attribute_name, value in self.attributes.__dict__.items():
            if value is None:
                continue
            name = self._format_attribute_name(attribute_name)
            value = self._format_attribute_value(attribute_name, value)
            s += f'\n{name}: {value}'
        return s
