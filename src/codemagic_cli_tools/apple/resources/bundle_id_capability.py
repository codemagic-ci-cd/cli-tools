from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Dict, Optional

from .resource import AbstractRelationships
from .resource import Relationship
from .resource import Resource


class CapabilityType(enum.Enum):
    ACCESS_WIFI_INFORMATION = 'ACCESS_WIFI_INFORMATION'
    APP_GROUPS = 'APP_GROUPS'
    APPLE_PAY = 'APPLE_PAY'
    ASSOCIATED_DOMAINS = 'ASSOCIATED_DOMAINS'
    AUTOFILL_CREDENTIAL_PROVIDER = 'AUTOFILL_CREDENTIAL_PROVIDER'
    CLASSKIT = 'CLASSKIT'
    DATA_PROTECTION = 'DATA_PROTECTION'
    GAME_CENTER = 'GAME_CENTER'
    HEALTHKIT = 'HEALTHKIT'
    HOMEKIT = 'HOMEKIT'
    HOT_SPOT = 'HOT_SPOT'
    ICLOUD = 'ICLOUD'
    IN_APP_PURCHASE = 'IN_APP_PURCHASE'
    INTER_APP_AUDIO = 'INTER_APP_AUDIO'
    MAPS = 'MAPS'
    MULTIPATH = 'MULTIPATH'
    NETWORK_EXTENSIONS = 'NETWORK_EXTENSIONS'
    NFC_TAG_READING = 'NFC_TAG_READING'
    PERSONAL_VPN = 'PERSONAL_VPN'
    PUSH_NOTIFICATIONS = 'PUSH_NOTIFICATIONS'
    SIRIKIT = 'SIRIKIT'
    WALLET = 'WALLET'
    WIRELESS_ACCESSORY_CONFIGURATION = 'WIRELESS_ACCESSORY_CONFIGURATION'


@dataclass
class CapabilityOption:
    class Key(enum.Enum):
        XCODE_5 = 'XCODE_5'
        XCODE_6 = 'XCODE_6'
        COMPLETE_PROTECTION = 'COMPLETE_PROTECTION'
        PROTECTED_UNLESS_OPEN = 'PROTECTED_UNLESS_OPEN'
        PROTECTED_UNTIL_FIRST_USER_AUTH = 'PROTECTED_UNTIL_FIRST_USER_AUTH'

    description: str
    enabled: bool
    enabledByDefault: bool
    key: Key
    name: str
    supportsWildcard: bool

    @classmethod
    def from_api_response(cls, api_options: Optional[Dict]) -> Optional[CapabilityOption]:
        if api_options is None:
            return None
        options = api_options
        return CapabilityOption(
            description=options['description'],
            enabled=options['enabled'],
            enabledByDefault=options['enabledByDefault'],
            key=CapabilityOption.Key(options['key']),
            name=options['name'],
            supportsWildcard=options['supportsWildcard'],
        )

    def dict(self):
        d = self.__dict__
        d['key'] = self.key.value
        return d


@dataclass
class CapabilitySetting:
    class AllowedInstance(enum.Enum):
        ENTRY = 'ENTRY'
        SINGLE = 'SINGLE'
        MULTIPLE = 'MULTIPLE'

    class Key(enum.Enum):
        ICLOUD_VERSION = 'ICLOUD_VERSION'
        DATA_PROTECTION_PERMISSION_LEVEL = 'DATA_PROTECTION_PERMISSION_LEVEL'

    allowedInstances: AllowedInstance
    description: str
    enabledByDefault: bool
    key: Key
    name: str
    options: Optional[CapabilityOption]
    visible: bool
    minInstances: int

    @classmethod
    def from_api_response(cls, api_settings: Optional[Dict]) -> Optional[CapabilitySetting]:
        if api_settings is None:
            return None
        settings = api_settings
        return CapabilitySetting(
            allowedInstances=CapabilitySetting.AllowedInstance(settings['allowedInstances']),
            description=settings['description'],
            enabledByDefault=settings['enabledByDefault'],
            key=CapabilitySetting.Key(settings['key']),
            name=settings['name'],
            options=CapabilityOption.from_api_response(settings['options']),
            visible=settings['visible'],
            minInstances=settings['minInstances'],
        )

    def dict(self):
        d = self.__dict__
        d['allowedInstances'] = self.allowedInstances.value
        d['key'] = self.key.value
        d['options'] = self.options.dict()
        return d


class BundleIdCapability(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/bundleidcapability
    """

    @dataclass
    class Attributes(Resource.Attributes):
        capabilityType: CapabilityType
        settings: Optional[CapabilitySetting]

        @classmethod
        def from_api_response(cls, api_response: Dict) -> BundleIdCapability.Attributes:
            attributes = api_response['attributes']
            return BundleIdCapability.Attributes(
                capabilityType=CapabilityType(attributes['capabilityType']),
                settings=CapabilitySetting.from_api_response(attributes['settings']),
            )

        def dict(self) -> Dict:
            settings = None
            if self.settings is not None:
                settings = self.settings.dict()
            return {
                'capabilityType': self.capabilityType.value,
                'settings': settings
            }

    @dataclass
    class Relationships(AbstractRelationships):
        bundleId: Relationship

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: BundleIdCapability.Attributes = BundleIdCapability.Attributes.from_api_response(api_response)
        self.relationships: BundleIdCapability.Relationships = \
            BundleIdCapability.Relationships.from_api_response(api_response)
