from __future__ import annotations

import pathlib
import plistlib
import zipfile
from typing import List
from unittest import mock

import pytest

from codemagic.apple.app_store_connect.builds import Builds
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage
from codemagic.tools import AppStoreConnect


def _create_ipa(directory: pathlib.Path, supported_platforms: List[str]) -> Ipa:
    ipa_path = directory / "app.ipa"
    info_plist = {
        "CFBundleIdentifier": "io.codemagic.app",
        "CFBundleShortVersionString": "1.2.3",
        "CFBundleSupportedPlatforms": supported_platforms,
        "CFBundleVersion": "42",
    }
    with zipfile.ZipFile(ipa_path, "w") as zf:
        zf.writestr("Payload/App.app/Info.plist", plistlib.dumps(info_plist))
    return Ipa(ipa_path)


@pytest.mark.parametrize(
    ("supported_platforms", "expected_platform"),
    (
        (["iPhoneOS"], Platform.IOS),
        (["AppleTVOS"], Platform.TV_OS),
        (["XROS"], Platform.VISION_OS),
    ),
)
def test_ipa_platform(tmp_path: pathlib.Path, supported_platforms: List[str], expected_platform: Platform):
    ipa = _create_ipa(tmp_path, supported_platforms)

    assert AppStoreConnect._get_application_package_platform(ipa) is expected_platform


def test_macos_package_platform():
    macos_package = mock.create_autospec(MacOsPackage, instance=True)

    assert AppStoreConnect._get_application_package_platform(macos_package) is Platform.MAC_OS


def test_find_build_for_visionos_ipa(tmp_path: pathlib.Path, mock_app_store_connect: AppStoreConnect):
    ipa = _create_ipa(tmp_path, ["XROS"])
    build = mock.Mock(id="1525e3c9-3015-407a-9ba5-9addd2558224")
    mock_api_client = mock.Mock()
    mock_api_client.builds.Filter = Builds.Filter
    mock_api_client.builds.list.return_value = [build]

    with mock.patch.object(AppStoreConnect, "api_client", new_callable=mock.PropertyMock) as mock_api_client_property:
        mock_api_client_property.return_value = mock_api_client
        found_build = mock_app_store_connect._find_build(
            ResourceId("1234567890"),
            ipa,
            max_find_build_minutes=0,
            retry_wait_seconds=0,
        )

    assert found_build is build
    builds_filter = mock_api_client.builds.list.call_args[0][0]
    assert builds_filter.as_query_params() == {
        "filter[app]": "1234567890",
        "filter[version]": "42",
        "filter[preReleaseVersion.version]": "1.2.3",
        "filter[preReleaseVersion.platform]": "VISION_OS",
    }
