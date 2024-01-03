import pytest
from codemagic.apple.resources import CapabilityType


@pytest.mark.parametrize(
    ("capability_type", "expected_display_name"),
    (
        (CapabilityType.ACCESS_WIFI_INFORMATION, "Access Wi-Fi Information"),
        (CapabilityType.APPLE_ID_AUTH, "Sign In with Apple"),
        (CapabilityType.APPLE_PAY, "Apple Pay"),
        (CapabilityType.APP_GROUPS, "App Groups"),
        (CapabilityType.ASSOCIATED_DOMAINS, "Associated Domains"),
        (CapabilityType.AUTOFILL_CREDENTIAL_PROVIDER, "Autofill Credential Provider"),
        (CapabilityType.CLASSKIT, "ClassKit"),
        (CapabilityType.COREMEDIA_HLS_LOW_LATENCY, "Low Latency HLS"),
        (CapabilityType.DATA_PROTECTION, "Data Protection"),
        (CapabilityType.GAME_CENTER, "Game Center"),
        (CapabilityType.HEALTHKIT, "HealthKit"),
        (CapabilityType.HOMEKIT, "HomeKit"),
        (CapabilityType.HOT_SPOT, "Hotspot"),
        (CapabilityType.ICLOUD, "iCloud"),
        (CapabilityType.INTER_APP_AUDIO, "Inter-App Audio"),
        (CapabilityType.IN_APP_PURCHASE, "In-App Purchase"),
        (CapabilityType.MAPS, "Maps"),
        (CapabilityType.MULTIPATH, "Multipath"),
        (CapabilityType.NETWORK_CUSTOM_PROTOCOL, "Custom Network Protocol"),
        (CapabilityType.NETWORK_EXTENSIONS, "Network Extensions"),
        (CapabilityType.NFC_TAG_READING, "NFC Tag Reading"),
        (CapabilityType.PERSONAL_VPN, "Personal VPN"),
        (CapabilityType.PUSH_NOTIFICATIONS, "Push Notifications"),
        (CapabilityType.SIRIKIT, "SiriKit"),
        (CapabilityType.SYSTEM_EXTENSION_INSTALL, "System Extension"),
        (CapabilityType.USER_MANAGEMENT, "User Management"),
        (CapabilityType.WALLET, "Wallet"),
        (CapabilityType.WIRELESS_ACCESSORY_CONFIGURATION, "Wireless Accessory Configuration"),
    ),
)
def test_display_name(capability_type: CapabilityType, expected_display_name: str):
    assert capability_type.display_name == expected_display_name


@pytest.mark.parametrize(
    ("display_name", "expected_capability_type"),
    (
        ("Access Wi-Fi Information", CapabilityType.ACCESS_WIFI_INFORMATION),
        ("Sign In with Apple", CapabilityType.APPLE_ID_AUTH),
        ("Apple Pay", CapabilityType.APPLE_PAY),
        ("App Groups", CapabilityType.APP_GROUPS),
        ("Associated Domains", CapabilityType.ASSOCIATED_DOMAINS),
        ("Autofill Credential Provider", CapabilityType.AUTOFILL_CREDENTIAL_PROVIDER),
        ("ClassKit", CapabilityType.CLASSKIT),
        ("Low Latency HLS", CapabilityType.COREMEDIA_HLS_LOW_LATENCY),
        ("Data Protection", CapabilityType.DATA_PROTECTION),
        ("Game Center", CapabilityType.GAME_CENTER),
        ("HealthKit", CapabilityType.HEALTHKIT),
        ("HomeKit", CapabilityType.HOMEKIT),
        ("Hotspot", CapabilityType.HOT_SPOT),
        ("iCloud", CapabilityType.ICLOUD),
        ("Inter-App Audio", CapabilityType.INTER_APP_AUDIO),
        ("In-App Purchase", CapabilityType.IN_APP_PURCHASE),
        ("Maps", CapabilityType.MAPS),
        ("Multipath", CapabilityType.MULTIPATH),
        ("Custom Network Protocol", CapabilityType.NETWORK_CUSTOM_PROTOCOL),
        ("Network Extensions", CapabilityType.NETWORK_EXTENSIONS),
        ("NFC Tag Reading", CapabilityType.NFC_TAG_READING),
        ("Personal VPN", CapabilityType.PERSONAL_VPN),
        ("Push Notifications", CapabilityType.PUSH_NOTIFICATIONS),
        ("SiriKit", CapabilityType.SIRIKIT),
        ("System Extension", CapabilityType.SYSTEM_EXTENSION_INSTALL),
        ("User Management", CapabilityType.USER_MANAGEMENT),
        ("Wallet", CapabilityType.WALLET),
        ("Wireless Accessory Configuration", CapabilityType.WIRELESS_ACCESSORY_CONFIGURATION),
    ),
)
def test_from_display_name(display_name: str, expected_capability_type: CapabilityType):
    capability_type = CapabilityType.from_display_name(display_name)
    assert capability_type is expected_capability_type
