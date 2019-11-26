from __future__ import annotations

import enum
from typing import NamedTuple, Dict

from .resource import Relationship, Resource


class BundleIdPlatform(enum.Enum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'


class BundleId(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/bundleid
    """

    class Attributes(NamedTuple):
        identifier: str
        name: str
        platform: BundleIdPlatform
        seedId: str

        @classmethod
        def from_api_response(cls, api_response: Dict) -> BundleId.Attributes:
            attributes = api_response['attributes']
            return BundleId.Attributes(
                identifier=attributes['identifier'],
                name=attributes['name'],
                platform=BundleIdPlatform(attributes['platform']),
                seedId=attributes['seedId'],
            )

        def dict(self) -> Dict:
            d = self._asdict()
            d['platform'] = self.platform.value
            return d

    class Relationships(NamedTuple):
        profiles: Relationship
        bundleIdCapabilities: Relationship

        @classmethod
        def from_api_response(cls, api_response: Dict) -> BundleId.Relationships:
            return Relationship.create_relationships(BundleId.Relationships, api_response)

        def dict(self) -> Dict:
            return {
                'profiles': self.profiles.dict(),
                'bundleIdCapabilities': self.bundleIdCapabilities.dict()
            }

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes = BundleId.Attributes.from_api_response(api_response)
        self.relationships = BundleId.Relationships.from_api_response(api_response)
