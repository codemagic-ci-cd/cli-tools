from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resource import DictSerializable
from .resource import Relationship
from .resource import Resource
from .resource import ResourceEnum


class CapabilityType(ResourceEnum):
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
class CapabilityOption(DictSerializable):
    class Key(ResourceEnum):
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

    def __post_init__(self):
        if isinstance(self.key, str):
            self.key = CapabilityOption.Key(self.key)


@dataclass
class CapabilitySetting(DictSerializable):
    class AllowedInstance(ResourceEnum):
        ENTRY = 'ENTRY'
        SINGLE = 'SINGLE'
        MULTIPLE = 'MULTIPLE'

    class Key(ResourceEnum):
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

    def __post_init__(self):
        if isinstance(self.allowedInstances, str):
            self.allowedInstances = CapabilitySetting.AllowedInstance(self.allowedInstances)
        if isinstance(self.options, dict):
            self.options = CapabilityOption(**self.options)


class BundleIdCapability(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/bundleidcapability
    """

    @dataclass
    class Attributes(Resource.Attributes):
        capabilityType: CapabilityType
        settings: Optional[CapabilitySetting]

        def __post_init__(self):
            if isinstance(self.capabilityType, str):
                self.capabilityType = CapabilityType(self.capabilityType)
            if isinstance(self.settings, dict):
                self.settings = CapabilitySetting(**self.settings)

    @dataclass
    class Relationships(Resource.Relationships):
        bundleId: Relationship
