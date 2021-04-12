from __future__ import annotations

import enum
from typing import Optional


class _ResourceEnum(enum.Enum):

    def __str__(self):
        return str(self.value)


class AppStoreState(_ResourceEnum):
    DEVELOPER_REMOVED_FROM_SALE = 'DEVELOPER_REMOVED_FROM_SALE'
    DEVELOPER_REJECTED = 'DEVELOPER_REJECTED'
    IN_REVIEW = 'IN_REVIEW'
    INVALID_BINARY = 'INVALID_BINARY'
    METADATA_REJECTED = 'METADATA_REJECTED'
    PENDING_APPLE_RELEASE = 'PENDING_APPLE_RELEASE'
    PENDING_CONTRACT = 'PENDING_CONTRACT'
    PENDING_DEVELOPER_RELEASE = 'PENDING_DEVELOPER_RELEASE'
    PREPARE_FOR_SUBMISSION = 'PREPARE_FOR_SUBMISSION'
    PREORDER_READY_FOR_SALE = 'PREORDER_READY_FOR_SALE'
    PROCESSING_FOR_APP_STORE = 'PROCESSING_FOR_APP_STORE'
    READY_FOR_SALE = 'READY_FOR_SALE'
    REJECTED = 'REJECTED'
    REMOVED_FROM_SALE = 'REMOVED_FROM_SALE'
    WAITING_FOR_EXPORT_COMPLIANCE = 'WAITING_FOR_EXPORT_COMPLIANCE'
    WAITING_FOR_REVIEW = 'WAITING_FOR_REVIEW'
    REPLACED_WITH_NEW_VERSION = 'REPLACED_WITH_NEW_VERSION'


class BuildProcessingState(_ResourceEnum):
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    INVALID = 'INVALID'
    VALID = 'VALID'


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
    DEVELOPMENT = 'DEVELOPMENT'
    DISTRIBUTION = 'DISTRIBUTION'
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
        elif profile_type is profile_type.TVOS_APP_DEVELOPMENT:
            return CertificateType.DEVELOPMENT
        elif profile_type is profile_type.TVOS_APP_STORE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.TVOS_APP_ADHOC:
            return CertificateType.DISTRIBUTION
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


class Platform(_ResourceEnum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'
    TV_OS = 'TV_OS'


class ProfileState(_ResourceEnum):
    ACTIVE = 'ACTIVE'
    INVALID = 'INVALID'
    EXPIRED = 'EXPIRED'  # Undocumented Profile State


class ProfileType(_ResourceEnum):
    IOS_APP_ADHOC = 'IOS_APP_ADHOC'
    IOS_APP_DEVELOPMENT = 'IOS_APP_DEVELOPMENT'
    IOS_APP_INHOUSE = 'IOS_APP_INHOUSE'
    IOS_APP_STORE = 'IOS_APP_STORE'
    MAC_APP_DEVELOPMENT = 'MAC_APP_DEVELOPMENT'
    MAC_APP_DIRECT = 'MAC_APP_DIRECT'
    MAC_APP_STORE = 'MAC_APP_STORE'
    MAC_CATALYST_APP_DEVELOPMENT = 'MAC_CATALYST_APP_DEVELOPMENT'
    MAC_CATALYST_APP_DIRECT = 'MAC_CATALYST_APP_DIRECT'
    MAC_CATALYST_APP_STORE = 'MAC_CATALYST_APP_STORE'
    TVOS_APP_ADHOC = 'TVOS_APP_ADHOC'
    TVOS_APP_DEVELOPMENT = 'TVOS_APP_DEVELOPMENT'
    TVOS_APP_INHOUSE = 'TVOS_APP_INHOUSE'
    TVOS_APP_STORE = 'TVOS_APP_STORE'

    @property
    def is_ad_hoc_type(self) -> bool:
        return self.value.endswith('_ADHOC')

    @property
    def is_development_type(self) -> bool:
        return self.value.endswith('_DEVELOPMENT')

    @property
    def is_macos_profile(self) -> bool:
        return self.value.startswith('MAC_')

    def devices_not_allowed(self) -> bool:
        return not self.devices_allowed()

    def devices_allowed(self) -> bool:
        return self.is_development_type or self.is_ad_hoc_type


class ReleaseType(_ResourceEnum):
    MANUAL = 'MANUAL'
    AFTER_APPROVAL = 'AFTER_APPROVAL'
    SCHEDULED = 'SCHEDULED'


class ResourceType(_ResourceEnum):
    APP_STORER_VERSIONS = 'appStoreVersions'
    BUILDS = 'builds'
    BUNDLE_ID = 'bundleIds'
    BUNDLE_ID_CAPABILITIES = 'bundleIdCapabilities'
    CERTIFICATES = 'certificates'
    DEVICES = 'devices'
    PRE_RELEASE_VERSIONS = 'preReleaseVersions'
    PROFILES = 'profiles'
