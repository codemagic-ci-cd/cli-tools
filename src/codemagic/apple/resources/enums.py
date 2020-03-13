from __future__ import annotations

import enum
from typing import Optional


class _ResourceEnum(enum.Enum):

    def __str__(self):
        return str(self.value)


class BundleIdPlatform(_ResourceEnum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'
    UNIVERSAL = 'UNIVERSAL'


class CapabilityOptionKey(_ResourceEnum):
    XCODE_5 = 'XCODE_5'
    XCODE_6 = 'XCODE_6'
    COMPLETE_PROTECTION = 'COMPLETE_PROTECTION'
    PROTECTED_UNLESS_OPEN = 'PROTECTED_UNLESS_OPEN'
    PROTECTED_UNTIL_FIRST_USER_AUTH = 'PROTECTED_UNTIL_FIRST_USER_AUTH'


class CapabilitySettingAllowedInstance(_ResourceEnum):
    ENTRY = 'ENTRY'
    SINGLE = 'SINGLE'
    MULTIPLE = 'MULTIPLE'


class CapabilitySettingKey(_ResourceEnum):
    ICLOUD_VERSION = 'ICLOUD_VERSION'
    DATA_PROTECTION_PERMISSION_LEVEL = 'DATA_PROTECTION_PERMISSION_LEVEL'


class CapabilityType(_ResourceEnum):
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


class CertificateType(_ResourceEnum):
    DEVELOPER_ID_APPLICATION = 'DEVELOPER_ID_APPLICATION'
    DEVELOPER_ID_KEXT = 'DEVELOPER_ID_KEXT'
    IOS_DEVELOPMENT = 'IOS_DEVELOPMENT'
    IOS_DISTRIBUTION = 'IOS_DISTRIBUTION'
    MAC_APP_DEVELOPMENT = 'MAC_APP_DEVELOPMENT'
    MAC_APP_DISTRIBUTION = 'MAC_APP_DISTRIBUTION'
    MAC_INSTALLER_DISTRIBUTION = 'MAC_INSTALLER_DISTRIBUTION'

    @classmethod
    def from_profile_type(cls, profile_type: ProfileType) -> Optional[CertificateType]:
        if profile_type is profile_type.IOS_APP_ADHOC:
            return CertificateType.IOS_DISTRIBUTION
        elif profile_type is profile_type.IOS_APP_DEVELOPMENT:
            return CertificateType.IOS_DEVELOPMENT
        elif profile_type is profile_type.IOS_APP_STORE:
            return CertificateType.IOS_DISTRIBUTION
        elif profile_type is profile_type.MAC_APP_DEVELOPMENT:
            return CertificateType.MAC_APP_DEVELOPMENT
        elif profile_type is profile_type.MAC_APP_STORE:
            return CertificateType.MAC_APP_DISTRIBUTION
        else:
            raise ValueError(f'Certificate type for profile type {profile_type} is unknown')


class DeviceClass(_ResourceEnum):
    APPLE_TV = 'APPLE_TV'
    APPLE_WATCH = 'APPLE_WATCH'
    IPAD = 'IPAD'
    IPHONE = 'IPHONE'
    IPOD = 'IPOD'
    MAC = 'MAC'


class DeviceStatus(_ResourceEnum):
    DISABLED = 'DISABLED'
    ENABLED = 'ENABLED'


class ProfileState(_ResourceEnum):
    ACTIVE = 'ACTIVE'
    INVALID = 'INVALID'


class ProfileType(_ResourceEnum):
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

    def devices_not_allowed(self) -> bool:
        return self in (ProfileType.IOS_APP_STORE, ProfileType.IOS_APP_INHOUSE)

    def devices_allowed(self) -> bool:
        return not self.devices_not_allowed()


class ResourceType(_ResourceEnum):
    BUNDLE_ID = 'bundleIds'
    BUNDLE_ID_CAPABILITIES = 'bundleIdCapabilities'
    CERTIFICATES = 'certificates'
    DEVICES = 'devices'
    PROFILES = 'profiles'
