import enum
import json
from collections import OrderedDict
from typing import Dict, NamedTuple, Optional, List, Iterator, NewType

ResourceId = NewType('ResourceId', str)


class ResourceType(enum.Enum):
    APP = 'apps'
    BUNDLE_ID = 'bundleIds'


class Links(NamedTuple):
    self: str
    related: Optional[str] = None

    def dict(self) -> OrderedDict:
        return OrderedDict((k, v) for k, v in self._asdict().items() if v is not None)


class Paging(NamedTuple):
    total: int
    limit: int

    def dict(self) -> OrderedDict:
        return self._asdict()


class Meta(NamedTuple):
    paging: Paging

    def dict(self) -> OrderedDict:
        return OrderedDict(paging=self.paging.dict())


class Relationship(NamedTuple):
    name: str
    links: Links
    meta: Optional[Meta] = None

    def dict(self) -> OrderedDict:
        d = OrderedDict(links=self.links.dict())
        if self.meta is not None:
            d['meta'] = self.meta.dict()
        return d


class DefaultAttributes(NamedTuple):
    def dict(self) -> OrderedDict:
        return OrderedDict()


class Resource:

    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.type = ResourceType(api_response['type'])
        self.id: ResourceId = api_response['id']
        self.attributes = DefaultAttributes()
        self.relationships: List[Relationship] = list(self._gather_relationships(api_response))
        self.links: Links = Links(**api_response['links'])

    @classmethod
    def _gather_relationships(cls, api_response) -> Iterator[Relationship]:
        for name, relationship in api_response['relationships'].items():
            meta, links = None, None
            if 'meta' in relationship:
                paging = Paging(**relationship['meta']['paging'])
                meta = Meta(paging=paging)
            if 'links' in relationship:
                links = Links(**relationship['links'])
            yield Relationship(name=name, links=links, meta=meta)

    def dict(self):
        return OrderedDict(
            type=self.type.value,
            id=self.id,
            attributes=self.attributes.dict(),
            relationships=OrderedDict(
                (relationship.name, relationship.dict())
                for relationship in self.relationships
            ),
            links=self.links.dict()
        )

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
