from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from .bundle_id import BundleIdPlatform
from .resource import AbstractRelationships
from .resource import Relationship
from .resource import Resource


class ProfileState(enum.Enum):
    ACTIVE = 'ACTIVE'
    INVALID = 'INVALID'


class ProfileType(enum.Enum):
    IOS_APP_ADHOC = 'IOS_APP_ADHOC'
    IOS_APP_DEVELOPMENT = 'IOS_APP_DEVELOPMENT'
    IOS_APP_INHOUSE = 'IOS_APP_INHOUSE'
    IOS_APP_STORE = 'IOS_APP_STORE'
    MAC_APP_DEVELOPMENT = 'MAC_APP_DEVELOPMENT'
    MAC_APP_DIRECT = 'MAC_APP_DIRECT'
    MAC_APP_STORE = 'MAC_APP_STORE'
    TVOS_APP_ADHOC = 'TVOS_APP_ADHOC'
    TVOS_APP_DEVELOPMENT = 'TVOS_APP_DEVELOPMENT'
    TVOS_APP_INHOUSE = 'TVOS_APP_INHOUSE'
    TVOS_APP_STORE = 'TVOS_APP_STORE'


class Profile(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/profile
    """

    @dataclass
    class Attributes(Resource.Attributes):
        name: str
        platform: BundleIdPlatform
        profileContent: str
        uuid: str
        createdDate: Optional[datetime]
        profileState: ProfileState
        profileType: ProfileType
        expirationDate: datetime

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
    class Relationships(AbstractRelationships):
        certificates: Relationship
        devices: Relationship
        bundleId: Relationship

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: Profile.Attributes = Profile.Attributes.from_api_response(api_response)
        self.relationships: Profile.Relationships = Profile.Relationships.from_api_response(api_response)
