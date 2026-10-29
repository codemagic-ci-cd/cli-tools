from __future__ import annotations

from unittest import mock

import pytest

from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import SigningCertificate
from codemagic.tools import AppStoreConnect


@pytest.fixture
def app_store_connect() -> AppStoreConnect:
    return AppStoreConnect(
        issuer_id=IssuerId("issuer-id"),
        key_identifier=KeyIdentifier("key-identifier"),
        private_key="private-key",
    )


def test_find_usable_profiles_skips_profile_without_content(
    app_store_connect: AppStoreConnect,
    profile: Profile,
    profile_without_content: Profile,
    signing_certificate: SigningCertificate,
):
    with mock.patch.object(
        app_store_connect,
        "list_bundle_id_profiles",
        return_value=[profile_without_content, profile],
    ), mock.patch.object(
        app_store_connect,
        "_has_certificate",
        return_value=True,
    ) as mock_has_certificate:
        usable_profiles = app_store_connect._find_usable_profiles(
            [],
            [signing_certificate],
            ProfileType.IOS_APP_DEVELOPMENT,
            delete_stale_profiles=False,
        )

    assert usable_profiles == [profile]
    mock_has_certificate.assert_called_once_with(profile, {signing_certificate.id})
