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

        @classmethod
        def from_api_response(cls, api_response: Dict[str, Dict[str, str]]) -> Profile.Attributes:
            attributes = api_response['attributes']
            return Profile.Attributes(
                name=attributes['name'],
                platform=BundleIdPlatform(attributes['platform']),
                profileContent=attributes['profileContent'],
                uuid=attributes['uuid'],
                createdDate=Resource.from_iso_8601(attributes['createdDate']),
                profileState=ProfileState(attributes['profileState']),
                profileType=ProfileType(attributes['profileType']),
                expirationDate=Resource.from_iso_8601(attributes['expirationDate']),
            )

        def _get_str_value(self, field_name: str) -> Optional[str]:
            field_value = getattr(self, field_name)
            if field_value is None:
                return field_value
            elif isinstance(field_value, str):
                return field_value
            elif isinstance(field_value, enum.Enum):
                return field_value.value
            elif isinstance(field_value, datetime):
                return Resource.to_iso_8601(field_value)
            else:
                raise ValueError(f'Invalid value {field_value} on field {field_name}')

        def dict(self) -> Dict[str, Optional[str]]:
            return {field: self._get_str_value(field) for field in self.__dataclass_fields__}

    @dataclass
    class Relationships(AbstractRelationships):
        certificates: Relationship
        devices: Relationship
        bundleId: Relationship

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: Profile.Attributes = Profile.Attributes.from_api_response(api_response)
        self.relationships: Profile.Relationships = Profile.Relationships.from_api_response(api_response)
