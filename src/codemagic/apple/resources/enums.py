from __future__ import annotations

from typing import Tuple

from codemagic.cli import Colors
from codemagic.models.enums import ResourceEnum
from codemagic.utilities import log


class AppStoreState(ResourceEnum):
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

    @classmethod
    def editable_states(cls) -> Tuple[AppStoreState, ...]:
        return (
            AppStoreState.DEVELOPER_REJECTED,
            AppStoreState.INVALID_BINARY,
            AppStoreState.METADATA_REJECTED,
            AppStoreState.PREPARE_FOR_SUBMISSION,
            AppStoreState.REJECTED,
            AppStoreState.WAITING_FOR_REVIEW,
        )


class BetaReviewState(ResourceEnum):
    APPROVED = 'APPROVED'
    IN_REVIEW = 'IN_REVIEW'
    REJECTED = 'REJECTED'
    WAITING_FOR_REVIEW = 'WAITING_FOR_REVIEW'


class BuildProcessingState(ResourceEnum):
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    INVALID = 'INVALID'
    VALID = 'VALID'


class BundleIdPlatform(ResourceEnum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'
    UNIVERSAL = 'UNIVERSAL'
    SERVICES = 'SERVICES'


class CapabilityOptionKey(ResourceEnum):
    XCODE_5 = 'XCODE_5'
    XCODE_6 = 'XCODE_6'
    COMPLETE_PROTECTION = 'COMPLETE_PROTECTION'
    PROTECTED_UNLESS_OPEN = 'PROTECTED_UNLESS_OPEN'
    PROTECTED_UNTIL_FIRST_USER_AUTH = 'PROTECTED_UNTIL_FIRST_USER_AUTH'


class CapabilitySettingAllowedInstance(ResourceEnum):
    ENTRY = 'ENTRY'
    SINGLE = 'SINGLE'
    MULTIPLE = 'MULTIPLE'


class CapabilitySettingKey(ResourceEnum):
    ICLOUD_VERSION = 'ICLOUD_VERSION'
    DATA_PROTECTION_PERMISSION_LEVEL = 'DATA_PROTECTION_PERMISSION_LEVEL'


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


class CertificateType(ResourceEnum):
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
    def from_profile_type(cls, profile_type: ProfileType) -> CertificateType:
        if profile_type is profile_type.IOS_APP_ADHOC:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.IOS_APP_DEVELOPMENT:
            return CertificateType.IOS_DEVELOPMENT
        elif profile_type is profile_type.IOS_APP_STORE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.MAC_APP_DEVELOPMENT:
            return CertificateType.MAC_APP_DEVELOPMENT
        elif profile_type is profile_type.MAC_APP_STORE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.MAC_APP_DIRECT:
            return CertificateType.DEVELOPER_ID_APPLICATION
        elif profile_type is profile_type.TVOS_APP_DEVELOPMENT:
            return CertificateType.DEVELOPMENT
        elif profile_type is profile_type.TVOS_APP_STORE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.TVOS_APP_ADHOC:
            return CertificateType.DISTRIBUTION
        else:
            raise ValueError(f'Certificate type for profile type {profile_type} is unknown')


class ContentRightsDeclaration(ResourceEnum):
    DOES_NOT_USE_THIRD_PARTY_CONTENT = 'DOES_NOT_USE_THIRD_PARTY_CONTENT'
    USES_THIRD_PARTY_CONTENT = 'USES_THIRD_PARTY_CONTENT'


class DeviceClass(ResourceEnum):
    APPLE_TV = 'APPLE_TV'
    APPLE_WATCH = 'APPLE_WATCH'
    IPAD = 'IPAD'
    IPHONE = 'IPHONE'
    IPOD = 'IPOD'
    MAC = 'MAC'

    def is_compatible(self, profile_type: ProfileType) -> bool:
        if profile_type.is_tvos_profile:
            return self is DeviceClass.APPLE_TV
        elif profile_type.is_macos_profile:
            return self is DeviceClass.MAC
        else:
            return self in (
                DeviceClass.APPLE_WATCH,
                DeviceClass.IPAD,
                DeviceClass.IPOD,
                DeviceClass.IPHONE,
            )


class DeviceStatus(ResourceEnum):
    DISABLED = 'DISABLED'
    ENABLED = 'ENABLED'


class Platform(ResourceEnum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'
    TV_OS = 'TV_OS'


class ProfileState(ResourceEnum):
    ACTIVE = 'ACTIVE'
    INVALID = 'INVALID'
    EXPIRED = 'EXPIRED'  # Undocumented Profile State


class ProfileType(ResourceEnum):
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
    def is_ios_profile(self) -> bool:
        return self.value.startswith('IOS_')

    @property
    def is_macos_profile(self) -> bool:
        return self.value.startswith('MAC_')

    @property
    def is_tvos_profile(self) -> bool:
        return self.value.startswith('TVOS_')

    def devices_not_allowed(self) -> bool:
        return not self.devices_required()

    def devices_allowed(self) -> bool:
        warning = (
            'Deprecation warning! Method '
            '"devices_allowed" is deprecated in favor of "devices_required" in version 0.31.3 '
            'and is subject for removal in future releases.'
        )
        log.get_logger(self.__class__).warning(Colors.YELLOW(warning))
        return self.devices_required()

    def devices_required(self) -> bool:
        return self.is_development_type or self.is_ad_hoc_type


class ReleaseType(ResourceEnum):
    MANUAL = 'MANUAL'
    AFTER_APPROVAL = 'AFTER_APPROVAL'
    SCHEDULED = 'SCHEDULED'


class ResourceType(ResourceEnum):
    APPS = 'apps'
    APP_CUSTOM_PRODUCT_PAGE_VERSIONS = 'appCustomProductPageVersions'
    APP_EVENTS = 'appEvents'
    APP_STORE_VERSIONS = 'appStoreVersions'
    APP_STORE_VERSION_EXPERIMENTS = 'appStoreVersionExperiments'
    APP_STORE_VERSION_LOCALIZATIONS = 'appStoreVersionLocalizations'
    APP_STORE_VERSION_SUBMISSIONS = 'appStoreVersionSubmissions'
    BETA_APP_LOCALIZATIONS = 'betaAppLocalizations'
    BETA_APP_REVIEW_DETAILS = 'betaAppReviewDetails'
    BETA_APP_REVIEW_SUBMISSIONS = 'betaAppReviewSubmissions'
    BETA_BUILD_LOCALIZATIONS = 'betaBuildLocalizations'
    BETA_GROUPS = 'betaGroups'
    BUILDS = 'builds'
    BUNDLE_ID = 'bundleIds'
    BUNDLE_ID_CAPABILITIES = 'bundleIdCapabilities'
    CERTIFICATES = 'certificates'
    DEVICES = 'devices'
    PRE_RELEASE_VERSIONS = 'preReleaseVersions'
    PROFILES = 'profiles'
    REVIEW_SUBMISSIONS = 'reviewSubmissions'
    REVIEW_SUBMISSION_ITEMS = 'reviewSubmissionItems'


class ReviewSubmissionState(ResourceEnum):
    CANCELING = 'CANCELING'
    COMPLETE = 'COMPLETE'
    COMPLETING = 'COMPLETING'
    IN_REVIEW = 'IN_REVIEW'
    READY_FOR_REVIEW = 'READY_FOR_REVIEW'
    UNRESOLVED_ISSUES = 'UNRESOLVED_ISSUES'
    WAITING_FOR_REVIEW = 'WAITING_FOR_REVIEW'


class ReviewSubmissionItemState(ResourceEnum):
    ACCEPTED = 'ACCEPTED'
    APPROVED = 'APPROVED'
    READY_FOR_REVIEW = 'READY_FOR_REVIEW'
    REJECTED = 'REJECTED'
    REMOVED = 'REMOVED'


class Locale(ResourceEnum):
    """
    Referenced in https://developer.apple.com/documentation/appstoreconnectapi/betaapplocalization/attributes#discussion
    """
    DA = 'da'
    DE_DE = 'de-DE'
    EL = 'el'
    EN_AU = 'en-AU'
    EN_CA = 'en-CA'
    EN_GB = 'en-GB'
    EN_US = 'en-US'
    ES_ES = 'es-ES'
    ES_MX = 'es-MX'
    FI = 'fi'
    FR_CA = 'fr-CA'
    FR_FR = 'fr-FR'
    ID = 'id'
    IT = 'it'
    JA = 'ja'
    KO = 'ko'
    MS = 'ms'
    NL_NL = 'nl-NL'
    NO = 'no'
    PT_BR = 'pt-BR'
    PT_PT = 'pt-PT'
    RU = 'ru'
    SV = 'sv'
    TH = 'th'
    TR = 'tr'
    VI = 'vi'
    ZH_HANS = 'zh-Hans'
    ZH_HANT = 'zh-Hant'
