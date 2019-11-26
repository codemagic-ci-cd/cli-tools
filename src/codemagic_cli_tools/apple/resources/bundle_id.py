from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Dict

from .resource import AbstractRelationships
from .resource import Relationship
from .resource import Resource


class BundleIdPlatform(enum.Enum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'


class BundleId(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/bundleid
    """

    @dataclass
    class Attributes(Resource.Attributes):
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
            d = self.__dict__
            d['platform'] = self.platform.value
            return d

    @dataclass
    class Relationships(AbstractRelationships):
        profiles: Relationship
        bundleIdCapabilities: Relationship

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: BundleId.Attributes = BundleId.Attributes.from_api_response(api_response)
        self.relationships: BundleId.Relationships = BundleId.Relationships.from_api_response(api_response)
