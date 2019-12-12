from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Optional

from .bundle_id import BundleIdPlatform
from .enums import ProfileState
from .enums import ProfileType
from .resource import Relationship
from .resource import Resource


class Profile(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/profile
    """

    @dataclass
    class Attributes(Resource.Attributes):
        name: str
        platform: BundleIdPlatform
        uuid: str
        createdDate: Optional[datetime]
        profileState: ProfileState
        profileType: ProfileType
        expirationDate: datetime
        profileContent: str = field(metadata={'hide': True})

        def __post_init__(self):
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.createdDate, str):
                self.createdDate = Resource.from_iso_8601(self.createdDate)
            if isinstance(self.profileState, str):
                self.profileState = ProfileState(self.profileState)
            if isinstance(self.profileType, str):
                self.profileType = ProfileType(self.profileType)
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)

    @dataclass
    class Relationships(Resource.Relationships):
        certificates: Relationship
        devices: Relationship
        bundleId: Relationship

    def get_display_info(self) -> str:
        return f'{self.attributes.profileType} profile {self.attributes.uuid}'

    @property
    def profile_content(self) -> bytes:
        return b64decode(self.attributes.profileContent)
