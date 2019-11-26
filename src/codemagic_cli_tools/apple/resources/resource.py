from __future__ import annotations

import enum
import json
from typing import Dict, NamedTuple, Optional, NewType, TypeVar, Generic

ResourceId = NewType('ResourceId', str)


class ResourceType(enum.Enum):
    APP = 'apps'
    BUNDLE_ID = 'bundleIds'
    BUNDLE_ID_CAPABILITIES = 'bundleIdCapabilities'
    PROFILES = 'profiles'


class PagingInformation(NamedTuple):
    class Paging(NamedTuple):
        total: int
        limit: int

        def dict(self) -> Dict:
            return self._asdict()

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

    def dict(self) -> Dict:
        return {'paging': self.paging.dict()}


class Links(NamedTuple):
    self: str
    related: Optional[str] = None

    @classmethod
    def from_api_response(cls, links: Dict) -> Links:
        return Links(**links)

    def dict(self) -> Dict:
        d = self._asdict()
        if self.related is None:
            d.pop('related')
        return d


class ResourceLinks(NamedTuple):
    self: str

    @classmethod
    def from_api_response(cls, resource_links: Dict) -> ResourceLinks:
        return ResourceLinks(**resource_links)

    def dict(self) -> Dict:
        return self._asdict()


class Data(NamedTuple):
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


RelationshipsT = TypeVar('RelationshipsT', bound=NamedTuple)


class Relationship(NamedTuple, Generic[RelationshipsT]):
    meta: Optional[PagingInformation]
    links: Links
    data: Optional[Data]

    @classmethod
    def create_relationships(cls, relationships_type: RelationshipsT, api_response: Dict) -> RelationshipsT:
        relationships = api_response['relationships']
        kwargs = {field: cls.from_api_response(relationships[field]) for field in relationships_type._fields}
        return relationships_type(**kwargs)

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


class Resource:
    class Attributes(NamedTuple):
        def dict(self):
            return {}

    class Relationships(NamedTuple):
        def dict(self):
            return {}

    def __init__(self, api_response: Dict):
        print(json.dumps(api_response, indent=4))
        self._raw = api_response
        self.type = ResourceType(api_response['type'])
        self.id: ResourceId = ResourceId(api_response['id'])
        self.links: ResourceLinks = ResourceLinks.from_api_response(api_response['links'])
        self.attributes = Resource.Attributes()
        self.relationships = Resource.Relationships()

    def dict(self) -> Dict:
        return {
            'type': self.type.value,
            'id': str(self.id),
            'links': self.links.dict(),
            'attributes': self.attributes.dict(),
            'relationships': self.relationships.dict(),
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
