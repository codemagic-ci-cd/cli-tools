from __future__ import annotations

import abc
import enum
import json
from dataclasses import dataclass, Field
from datetime import datetime
from typing import Dict, Optional, overload

from models import JsonSerializable


class ResourceId(str):
    pass


class ResourceType(enum.Enum):
    APP = 'apps'
    BUNDLE_ID = 'bundleIds'
    BUNDLE_ID_CAPABILITIES = 'bundleIdCapabilities'
    PROFILES = 'profiles'


@dataclass
class PagingInformation:
    @dataclass
    class Paging:
        total: int
        limit: int

        def dict(self) -> Dict[str, int]:
            return self.__dict__

    paging: Paging

    @classmethod
    def from_api_response(cls, api_response: Dict) -> Optional[PagingInformation]:
        try:
            paging_info = api_response['meta']
        except KeyError:
            return None
        return PagingInformation(
            paging=PagingInformation.Paging(**paging_info['paging'])
        )

    def dict(self) -> Dict[str, Dict[str, int]]:
        return {'paging': self.paging.dict()}


@dataclass
class Links:
    itself: str
    related: Optional[str] = None

    @classmethod
    def from_api_response(cls, links: Dict[str, str]) -> Links:
        return Links(itself=links['self'], related=links.get('related'))

    def dict(self) -> Dict:
        d = {'self': self.itself}
        if self.related is not None:
            d['related'] = self.related
        return d


@dataclass
class ResourceLinks:
    itself: str

    @classmethod
    def from_api_response(cls, resource_links: Dict) -> ResourceLinks:
        return ResourceLinks(itself=resource_links['self'])

    def dict(self) -> Dict[str, str]:
        return {'self': self.itself}


@dataclass
class Data:
    id: str
    type: ResourceType

    @classmethod
    def from_api_response(cls, api_response: Dict) -> Optional[Data]:
        try:
            data = api_response['data']
        except KeyError:
            return None
        return Data(id=data['id'], type=ResourceType(data['type']))

    def dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type.value
        }


@dataclass
class Relationship:

    meta: Optional[PagingInformation]
    links: Links
    data: Optional[Data]

    @classmethod
    def from_api_response(cls, api_relationship: Dict) -> Relationship:
        return Relationship(
            meta=PagingInformation.from_api_response(api_relationship),
            links=Links.from_api_response(api_relationship['links']),
            data=Data.from_api_response(api_relationship)
        )

    def dict(self) -> Dict:
        d = {'links': self.links.dict()}
        if self.meta is not None:
            d['meta'] = self.meta.dict()
        if self.data is not None:
            d['data'] = self.data.dict()
        return d


class AbstractRelationships(metaclass=abc.ABCMeta):
    __dataclass_fields__: Dict[str, Field] = {}

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def from_api_response(cls, api_response: Dict):
        relationships = api_response['relationships']
        kwargs = {
            field_name: Relationship.from_api_response(relationships[field_name])
            for field_name in cls.__dataclass_fields__
        }
        return cls(**kwargs)

    def dict(self) -> Dict:
        return {
            field_name: getattr(self, field_name).dict()
            for field_name in self.__dataclass_fields__
        }


class LinkedResourceData(JsonSerializable):

    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.type = ResourceType(api_response['type'])
        self.id: ResourceId = ResourceId(api_response['id'])

    def dict(self) -> Dict:
        return {
            'type': self.type.value,
            'id': str(self.id),
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class Resource(LinkedResourceData):
    class Attributes(metaclass=abc.ABCMeta):
        __dataclass_fields__: Dict[str, Field] = {}

        def dict(self):
            return {}

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.links: ResourceLinks = ResourceLinks.from_api_response(api_response['links'])
        self.attributes: Resource.Attributes = Resource.Attributes()
        self.relationships: AbstractRelationships = AbstractRelationships()

    def dict(self) -> Dict:
        return {
            **super().dict(),
            'links': self.links.dict(),
            'attributes': self.attributes.dict() if self.attributes else {},
            'relationships': self.relationships.dict() if self.relationships else {},
        }

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
