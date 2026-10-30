from __future__ import annotations

from unittest import mock

from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import SigningCertificate
from codemagic.tools import AppStoreConnect


def test_find_usable_profiles_skips_profile_without_content(
    mock_app_store_connect: AppStoreConnect,
    profile: Profile,
    profile_without_content: Profile,
    signing_certificate: SigningCertificate,
):
    with mock.patch.object(
        mock_app_store_connect,
        "list_bundle_id_profiles",
        return_value=[profile_without_content, profile],
    ), mock.patch.object(
        mock_app_store_connect,
        "_has_certificate",
        return_value=True,
    ) as mock_has_certificate:
        usable_profiles = mock_app_store_connect._find_usable_profiles(
            [],
            [signing_certificate],
            ProfileType.IOS_APP_DEVELOPMENT,
            delete_stale_profiles=False,
        )

    assert usable_profiles == [profile]
    mock_has_certificate.assert_called_once_with(profile, {signing_certificate.id})
