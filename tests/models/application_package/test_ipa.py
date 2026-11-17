from __future__ import annotations

import pathlib
import plistlib
import zipfile
from typing import List

import pytest

from codemagic.models.application_package import Ipa


def _create_ipa(directory: pathlib.Path, supported_platforms: List[str]) -> Ipa:
    ipa_path = directory / "app.ipa"
    info_plist = {
        "CFBundleIdentifier": "io.codemagic.app",
        "CFBundleSupportedPlatforms": supported_platforms,
    }
    with zipfile.ZipFile(ipa_path, "w") as zf:
        zf.writestr("Payload/App.app/Info.plist", plistlib.dumps(info_plist))
    return Ipa(ipa_path)


@pytest.mark.parametrize(
    ("supported_platforms", "expected_is_for_tvos", "expected_is_for_visionos"),
    (
        (["iPhoneOS"], False, False),
        (["AppleTVOS"], True, False),
        (["XROS"], False, True),
    ),
)
def test_target_platform(
    tmp_path: pathlib.Path,
    supported_platforms: List[str],
    expected_is_for_tvos: bool,
    expected_is_for_visionos: bool,
):
    ipa = _create_ipa(tmp_path, supported_platforms)

    assert ipa.is_for_tvos() is expected_is_for_tvos
    assert ipa.is_for_visionos() is expected_is_for_visionos
