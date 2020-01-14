from __future__ import annotations

from codemagic.apple.resources import BundleIdCapability


def test_bundle_id_capability_initialization(api_bundle_id_capability):
    bundle_id_capability = BundleIdCapability(api_bundle_id_capability)
    assert bundle_id_capability.dict() == api_bundle_id_capability
