from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource
from .resource import ResourceEnum


class BundleIdPlatform(ResourceEnum):
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

        def __post_init__(self):
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)

    @dataclass
    class Relationships(Resource.Relationships):
        profiles: Relationship
        bundleIdCapabilities: Relationship
