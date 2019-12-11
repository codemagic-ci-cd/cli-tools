from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
from typing import TYPE_CHECKING

from .enums import BundleIdPlatform
from .resource import Relationship
from .resource import Resource

if TYPE_CHECKING:
    from .profile import Profile


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

    def has_profile(self, profiles: Sequence[Profile]) -> bool:
        for profile in profiles:
            if profile.relationships.bundleId.data.id == self.id:
                return True
        return False
