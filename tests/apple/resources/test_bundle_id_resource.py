from __future__ import annotations

import pytest

from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import Profile


def test_bundle_id_initialization(api_bundle_id):
    bundle_id = BundleId(api_bundle_id)
    assert bundle_id.dict() == api_bundle_id


@pytest.mark.parametrize('profile_bundle_id, has', [('NLRN94JD59', True), ('BUNDLE-ID', False)])
def test_has_profile_true(api_bundle_id, api_profile, profile_bundle_id, has):
    bundle_id = BundleId(api_bundle_id)
    api_profile['relationships']['bundleId']['data']['id'] = profile_bundle_id
    assert bundle_id.has_profile([Profile(api_profile)]) is has
