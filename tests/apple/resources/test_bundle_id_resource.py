from __future__ import annotations

from codemagic.apple.resources import BundleId


def test_bundle_id_initialization(api_bundle_id):
    bundle_id = BundleId(api_bundle_id)
    assert bundle_id.dict() == api_bundle_id
