from __future__ import annotations

import pathlib
from typing import Callable
from typing import List

import pytest

from codemagic.models.altool.enums import PlatformType
from codemagic.models.application_package import Ipa


@pytest.mark.parametrize(
    ("supported_platforms", "expected_platform_type"),
    (
        (["iPhoneOS"], PlatformType.IOS),
        (["AppleTVOS"], PlatformType.APPLE_TV_OS),
        (["XROS"], PlatformType.VISION_OS),
    ),
)
def test_platform_type_from_ipa_path(
    create_ipa: Callable[[List[str]], Ipa],
    supported_platforms: List[str],
    expected_platform_type: PlatformType,
):
    ipa = create_ipa(supported_platforms)

    assert PlatformType.from_path(ipa.path) is expected_platform_type


def test_platform_type_from_pkg_path():
    assert PlatformType.from_path(pathlib.Path("app.pkg")) is PlatformType.MAC_OS


def test_platform_type_from_unknown_path():
    with pytest.raises(ValueError):
        PlatformType.from_path(pathlib.Path("app.zip"))
