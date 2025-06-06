from __future__ import annotations

import re
from collections import OrderedDict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic.models.enums import ResourceEnum
from codemagic.utilities.decorators import deprecated


class AppStoreState(ResourceEnum):
    DEVELOPER_REMOVED_FROM_SALE = "DEVELOPER_REMOVED_FROM_SALE"
    DEVELOPER_REJECTED = "DEVELOPER_REJECTED"
    IN_REVIEW = "IN_REVIEW"
    INVALID_BINARY = "INVALID_BINARY"
    METADATA_REJECTED = "METADATA_REJECTED"
    PENDING_APPLE_RELEASE = "PENDING_APPLE_RELEASE"
    PENDING_CONTRACT = "PENDING_CONTRACT"
    PENDING_DEVELOPER_RELEASE = "PENDING_DEVELOPER_RELEASE"
    PREPARE_FOR_SUBMISSION = "PREPARE_FOR_SUBMISSION"
    PREORDER_READY_FOR_SALE = "PREORDER_READY_FOR_SALE"
    PROCESSING_FOR_APP_STORE = "PROCESSING_FOR_APP_STORE"
    READY_FOR_SALE = "READY_FOR_SALE"
    REJECTED = "REJECTED"
    REMOVED_FROM_SALE = "REMOVED_FROM_SALE"
    WAITING_FOR_EXPORT_COMPLIANCE = "WAITING_FOR_EXPORT_COMPLIANCE"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    REPLACED_WITH_NEW_VERSION = "REPLACED_WITH_NEW_VERSION"

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
    APPROVED = "APPROVED"
    IN_REVIEW = "IN_REVIEW"
    REJECTED = "REJECTED"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"


class BuildProcessingState(ResourceEnum):
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    INVALID = "INVALID"
    VALID = "VALID"


class BuildAudienceType(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/buildaudiencetype
    """

    INTERNAL_ONLY = "INTERNAL_ONLY"
    APP_STORE_ELIGIBLE = "APP_STORE_ELIGIBLE"


class BundleIdPlatform(ResourceEnum):
    IOS = "IOS"
    MAC_OS = "MAC_OS"
    UNIVERSAL = "UNIVERSAL"
    SERVICES = "SERVICES"


class CapabilityOptionKey(ResourceEnum):
    XCODE_5 = "XCODE_5"
    XCODE_6 = "XCODE_6"
    COMPLETE_PROTECTION = "COMPLETE_PROTECTION"
    PROTECTED_UNLESS_OPEN = "PROTECTED_UNLESS_OPEN"
    PROTECTED_UNTIL_FIRST_USER_AUTH = "PROTECTED_UNTIL_FIRST_USER_AUTH"


class CapabilitySettingAllowedInstance(ResourceEnum):
    ENTRY = "ENTRY"
    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"


class CapabilitySettingKey(ResourceEnum):
    ICLOUD_VERSION = "ICLOUD_VERSION"
    DATA_PROTECTION_PERMISSION_LEVEL = "DATA_PROTECTION_PERMISSION_LEVEL"


class CapabilityType(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/capabilitytype
    """

    ACCESS_WIFI_INFORMATION = "ACCESS_WIFI_INFORMATION"
    APPLE_ID_AUTH = "APPLE_ID_AUTH"
    APPLE_PAY = "APPLE_PAY"
    APP_GROUPS = "APP_GROUPS"
    ASSOCIATED_DOMAINS = "ASSOCIATED_DOMAINS"
    AUTOFILL_CREDENTIAL_PROVIDER = "AUTOFILL_CREDENTIAL_PROVIDER"
    CLASSKIT = "CLASSKIT"
    COREMEDIA_HLS_LOW_LATENCY = "COREMEDIA_HLS_LOW_LATENCY"
    DATA_PROTECTION = "DATA_PROTECTION"
    GAME_CENTER = "GAME_CENTER"
    HEALTHKIT = "HEALTHKIT"
    HOMEKIT = "HOMEKIT"
    HOT_SPOT = "HOT_SPOT"
    ICLOUD = "ICLOUD"
    INTER_APP_AUDIO = "INTER_APP_AUDIO"
    IN_APP_PURCHASE = "IN_APP_PURCHASE"
    MAPS = "MAPS"
    MULTIPATH = "MULTIPATH"
    NETWORK_CUSTOM_PROTOCOL = "NETWORK_CUSTOM_PROTOCOL"
    NETWORK_EXTENSIONS = "NETWORK_EXTENSIONS"
    NETWORK_SLICING = "NETWORK_SLICING"
    NFC_TAG_READING = "NFC_TAG_READING"
    PERSONAL_VPN = "PERSONAL_VPN"
    PUSH_NOTIFICATIONS = "PUSH_NOTIFICATIONS"
    SIRIKIT = "SIRIKIT"
    SYSTEM_EXTENSION_INSTALL = "SYSTEM_EXTENSION_INSTALL"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    WALLET = "WALLET"
    WIRELESS_ACCESSORY_CONFIGURATION = "WIRELESS_ACCESSORY_CONFIGURATION"

    @classmethod
    def from_display_name(cls, display_name: str) -> CapabilityType:
        for capability_type in cls:
            if capability_type.display_name == display_name:
                return capability_type
        raise ValueError("Unknown capability type", display_name)

    @property
    def display_name(self) -> str:
        try:
            return {
                CapabilityType.ACCESS_WIFI_INFORMATION: "Access Wi-Fi Information",
                CapabilityType.APPLE_ID_AUTH: "Sign In with Apple",
                CapabilityType.COREMEDIA_HLS_LOW_LATENCY: "Low Latency HLS",
                CapabilityType.HOT_SPOT: "Hotspot",
                CapabilityType.ICLOUD: "iCloud",
                CapabilityType.INTER_APP_AUDIO: "Inter-App Audio",
                CapabilityType.IN_APP_PURCHASE: "In-App Purchase",
                CapabilityType.NETWORK_CUSTOM_PROTOCOL: "Custom Network Protocol",
                CapabilityType.NETWORK_SLICING: "5G Network Slicing",
                CapabilityType.NFC_TAG_READING: "NFC Tag Reading",
                CapabilityType.PERSONAL_VPN: "Personal VPN",
                CapabilityType.SYSTEM_EXTENSION_INSTALL: "System Extension",
            }[self]
        except KeyError:
            return self.get_default_display_name(self.value)

    @classmethod
    def get_default_display_name(cls, capability_type_value: str) -> str:
        parts = capability_type_value.split("_")
        title = " ".join(parts).title()
        return re.sub(r"(kit)$", "Kit", title)


class CertificateType(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/certificatetype
    """

    DEVELOPER_ID_APPLICATION = "DEVELOPER_ID_APPLICATION"
    DEVELOPER_ID_KEXT = "DEVELOPER_ID_KEXT"
    DEVELOPMENT = "DEVELOPMENT"
    DISTRIBUTION = "DISTRIBUTION"
    IOS_DEVELOPMENT = "IOS_DEVELOPMENT"
    IOS_DISTRIBUTION = "IOS_DISTRIBUTION"
    MAC_APP_DEVELOPMENT = "MAC_APP_DEVELOPMENT"
    MAC_APP_DISTRIBUTION = "MAC_APP_DISTRIBUTION"
    MAC_INSTALLER_DISTRIBUTION = "MAC_INSTALLER_DISTRIBUTION"

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
        elif profile_type is profile_type.MAC_CATALYST_APP_DEVELOPMENT:
            return CertificateType.DEVELOPMENT
        elif profile_type is profile_type.MAC_CATALYST_APP_STORE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.MAC_CATALYST_APP_DIRECT:
            return CertificateType.DEVELOPER_ID_APPLICATION
        elif profile_type is profile_type.IOS_APP_INHOUSE:
            return CertificateType.DISTRIBUTION
        elif profile_type is profile_type.TVOS_APP_INHOUSE:
            return CertificateType.DISTRIBUTION
        else:
            raise ValueError(f"Certificate type for profile type {profile_type} is unknown")

    @classmethod
    def resolve_applicable_types(
        cls,
        certificate_types: Optional[Union[CertificateType, Sequence[CertificateType]]] = None,
        profile_type: Optional[ProfileType] = None,
    ) -> List[CertificateType]:
        """
        Construct a list of unique certificate types based on the provided certificate and
        provisioning profile types. Resolved types are ordered so that
        - provided `certificate_types` come first in original ordering (if given),
        - which is followed by `profile_type` primary accompanying certificate type and
          finally `profile_type`'s secondary matching certificate type in case it exists.
        """

        types: List[CertificateType] = []

        if isinstance(certificate_types, CertificateType):
            types.append(certificate_types)
        elif certificate_types:
            types.extend(certificate_types)

        if profile_type:
            types.append(CertificateType.from_profile_type(profile_type))
            # Include iOS and Mac App distribution certificate types backwards compatibility.
            # In the past iOS and Mac App Store profiles used to map to iOS and Mac App distribution
            # certificates, and consequently they too can be used with those profiles.
            if profile_type is ProfileType.IOS_APP_STORE or profile_type is ProfileType.IOS_APP_ADHOC:
                types.append(CertificateType.IOS_DISTRIBUTION)
            elif profile_type is ProfileType.MAC_APP_STORE:
                types.append(CertificateType.MAC_APP_DISTRIBUTION)

        # Remove duplicate entries from the list in order-preserving way.
        return list(OrderedDict.fromkeys(types))


class ContentRightsDeclaration(ResourceEnum):
    DOES_NOT_USE_THIRD_PARTY_CONTENT = "DOES_NOT_USE_THIRD_PARTY_CONTENT"
    USES_THIRD_PARTY_CONTENT = "USES_THIRD_PARTY_CONTENT"


class DeviceClass(ResourceEnum):
    APPLE_SILICON_MAC = "APPLE_SILICON_MAC"
    APPLE_TV = "APPLE_TV"
    APPLE_VISION_PRO = "APPLE_VISION_PRO"
    APPLE_WATCH = "APPLE_WATCH"
    IPAD = "IPAD"
    IPHONE = "IPHONE"
    IPOD = "IPOD"
    MAC = "MAC"

    def is_compatible(self, profile_type: ProfileType) -> bool:
        if profile_type.is_tvos_profile:
            return self is DeviceClass.APPLE_TV
        elif profile_type.is_macos_profile:
            return self is DeviceClass.MAC
        else:
            return self in (
                DeviceClass.APPLE_VISION_PRO,
                DeviceClass.APPLE_WATCH,
                DeviceClass.IPAD,
                DeviceClass.IPOD,
                DeviceClass.IPHONE,
            )


class DeviceStatus(ResourceEnum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"


class ExternalBetaState(ResourceEnum):
    BETA_APPROVED = "BETA_APPROVED"
    BETA_REJECTED = "BETA_REJECTED"
    EXPIRED = "EXPIRED"
    IN_BETA_REVIEW = "IN_BETA_REVIEW"
    IN_BETA_TESTING = "IN_BETA_TESTING"
    IN_EXPORT_COMPLIANCE_REVIEW = "IN_EXPORT_COMPLIANCE_REVIEW"
    MISSING_EXPORT_COMPLIANCE = "MISSING_EXPORT_COMPLIANCE"
    PROCESSING = "PROCESSING"
    PROCESSING_EXCEPTION = "PROCESSING_EXCEPTION"
    READY_FOR_BETA_SUBMISSION = "READY_FOR_BETA_SUBMISSION"
    READY_FOR_BETA_TESTING = "READY_FOR_BETA_TESTING"
    WAITING_FOR_BETA_REVIEW = "WAITING_FOR_BETA_REVIEW"


class InternalBetaState(ResourceEnum):
    EXPIRED = "EXPIRED"
    IN_BETA_TESTING = "IN_BETA_TESTING"
    IN_EXPORT_COMPLIANCE_REVIEW = "IN_EXPORT_COMPLIANCE_REVIEW"
    MISSING_EXPORT_COMPLIANCE = "MISSING_EXPORT_COMPLIANCE"
    PROCESSING = "PROCESSING"
    PROCESSING_EXCEPTION = "PROCESSING_EXCEPTION"
    READY_FOR_BETA_TESTING = "READY_FOR_BETA_TESTING"


class PhasedReleaseState(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/phasedreleasestate
    """

    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    INACTIVE = "INACTIVE"
    PAUSED = "PAUSED"


class Platform(ResourceEnum):
    IOS = "IOS"
    MAC_OS = "MAC_OS"
    TV_OS = "TV_OS"


class ProfileState(ResourceEnum):
    ACTIVE = "ACTIVE"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"  # Undocumented Profile State


class ProfileType(ResourceEnum):
    IOS_APP_ADHOC = "IOS_APP_ADHOC"
    IOS_APP_DEVELOPMENT = "IOS_APP_DEVELOPMENT"
    IOS_APP_INHOUSE = "IOS_APP_INHOUSE"
    IOS_APP_STORE = "IOS_APP_STORE"
    MAC_APP_DEVELOPMENT = "MAC_APP_DEVELOPMENT"
    MAC_APP_DIRECT = "MAC_APP_DIRECT"
    MAC_APP_STORE = "MAC_APP_STORE"
    MAC_CATALYST_APP_DEVELOPMENT = "MAC_CATALYST_APP_DEVELOPMENT"
    MAC_CATALYST_APP_DIRECT = "MAC_CATALYST_APP_DIRECT"
    MAC_CATALYST_APP_STORE = "MAC_CATALYST_APP_STORE"
    TVOS_APP_ADHOC = "TVOS_APP_ADHOC"
    TVOS_APP_DEVELOPMENT = "TVOS_APP_DEVELOPMENT"
    TVOS_APP_INHOUSE = "TVOS_APP_INHOUSE"
    TVOS_APP_STORE = "TVOS_APP_STORE"

    @property
    def is_ad_hoc_type(self) -> bool:
        return self.value.endswith("_ADHOC")

    @property
    def is_development_type(self) -> bool:
        return self.value.endswith("_DEVELOPMENT")

    @property
    def is_ios_profile(self) -> bool:
        return self.value.startswith("IOS_")

    @property
    def is_macos_profile(self) -> bool:
        return self.value.startswith("MAC_")

    @property
    def is_tvos_profile(self) -> bool:
        return self.value.startswith("TVOS_")

    def devices_not_allowed(self) -> bool:
        return not self.devices_required()

    @deprecated("0.31.3", 'Use "ProfileType.devices_required" instead.')
    def devices_allowed(self) -> bool:
        return self.devices_required()

    def devices_required(self) -> bool:
        return self.is_development_type or self.is_ad_hoc_type


class ReleaseType(ResourceEnum):
    MANUAL = "MANUAL"
    AFTER_APPROVAL = "AFTER_APPROVAL"
    SCHEDULED = "SCHEDULED"


class ResourceType(ResourceEnum):
    APPS = "apps"
    APP_CUSTOM_PRODUCT_PAGE_VERSIONS = "appCustomProductPageVersions"
    APP_EVENTS = "appEvents"
    APP_STORE_VERSIONS = "appStoreVersions"
    APP_STORE_VERSION_EXPERIMENTS = "appStoreVersionExperiments"
    APP_STORE_VERSION_LOCALIZATIONS = "appStoreVersionLocalizations"
    APP_STORE_VERSION_PHASED_RELEASES = "appStoreVersionPhasedReleases"
    APP_STORE_VERSION_SUBMISSIONS = "appStoreVersionSubmissions"
    BETA_APP_LOCALIZATIONS = "betaAppLocalizations"
    BETA_APP_REVIEW_DETAILS = "betaAppReviewDetails"
    BETA_APP_REVIEW_SUBMISSIONS = "betaAppReviewSubmissions"
    BETA_BUILD_DETAILS = "buildBetaDetails"
    BETA_BUILD_LOCALIZATIONS = "betaBuildLocalizations"
    BETA_GROUPS = "betaGroups"
    BUILDS = "builds"
    BUNDLE_ID = "bundleIds"
    BUNDLE_ID_CAPABILITIES = "bundleIdCapabilities"
    CERTIFICATES = "certificates"
    DEVICES = "devices"
    PRE_RELEASE_VERSIONS = "preReleaseVersions"
    PROFILES = "profiles"
    REVIEW_SUBMISSIONS = "reviewSubmissions"
    REVIEW_SUBMISSION_ITEMS = "reviewSubmissionItems"


class ReviewSubmissionState(ResourceEnum):
    CANCELING = "CANCELING"
    COMPLETE = "COMPLETE"
    COMPLETING = "COMPLETING"
    IN_REVIEW = "IN_REVIEW"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    UNRESOLVED_ISSUES = "UNRESOLVED_ISSUES"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"


class ReviewSubmissionItemState(ResourceEnum):
    ACCEPTED = "ACCEPTED"
    APPROVED = "APPROVED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REJECTED = "REJECTED"
    REMOVED = "REMOVED"


class Locale(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/app_store/app_metadata/app_info_localizations/managing_metadata_in_your_app_by_using_locale_shortcodes
    """

    AR_SA = "ar-SA"  # Arabic
    CA = "ca"  # Catalan
    CS = "cs"  # Czech
    DA = "da"  # Danish
    DE_DE = "de-DE"  # German
    EL = "el"  # Greek
    EN_AU = "en-AU"  # English (Australia)
    EN_CA = "en-CA"  # English (Canada)
    EN_GB = "en-GB"  # English (U.K.)
    EN_US = "en-US"  # English (U.S.)
    ES_ES = "es-ES"  # Spanish (Spain)
    ES_MX = "es-MX"  # Spanish (Mexico)
    FI = "fi"  # Finnish
    FR_CA = "fr-CA"  # French (Canada)
    FR_FR = "fr-FR"  # French
    HE = "he"  # Hebrew
    HI = "hi"  # Hindi
    HR = "hr"  # Croatian
    HU = "hu"  # Hungarian
    ID = "id"  # Indonesian
    IT = "it"  # Italian
    JA = "ja"  # Japanese
    KO = "ko"  # Korean
    MS = "ms"  # Malay
    NL_NL = "nl-NL"  # Dutch
    NO = "no"  # Norwegian
    PL = "pl"  # Polish
    PT_BR = "pt-BR"  # Portuguese (Brazil)
    PT_PT = "pt-PT"  # Portuguese (Portugal)
    RO = "ro"  # Romanian
    RU = "ru"  # Russian
    SK = "sk"  # Slovak
    SV = "sv"  # Swedish
    TH = "th"  # Thai
    TR = "tr"  # Turkish
    UK = "uk"  # Ukrainian
    VI = "vi"  # Vietnamese
    ZH_HANS = "zh-Hans"  # Chinese (Simplified)
    ZH_HANT = "zh-Hant"  # Chinese (Traditional)


class SubscriptionStatusUrlVersion(ResourceEnum):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/subscriptionstatusurlversion
    """

    V1 = "V1"
    V2 = "V2"
    v1 = "v1"
    v2 = "v2"
