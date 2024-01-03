from __future__ import annotations

from codemagic.apple.resources import BundleIdCapability


def test_bundle_id_capability_initialization(api_bundle_id_capability):
    bundle_id_capability = BundleIdCapability(api_bundle_id_capability)
    assert bundle_id_capability.dict() == api_bundle_id_capability


def test_bundle_id_capability_string_representation(api_bundle_id_capability):
    """
    Check that for capability type the display name is shown
    """
    bundle_id_capability = BundleIdCapability(api_bundle_id_capability)
    expected_lines = (
        "Id: NLRN94JD59_GAME_CENTER_IOS",
        "Type: bundleIdCapabilities",
        "Capability type: Game Center",
    )
    assert str(bundle_id_capability) == "\n".join(expected_lines)
