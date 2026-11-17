from __future__ import annotations

from typing import Callable
from typing import List

import pytest

from codemagic.models.application_package import Ipa


@pytest.mark.parametrize(
    ("supported_platforms", "expected_is_for_tvos", "expected_is_for_visionos"),
    (
        (["iPhoneOS"], False, False),
        (["AppleTVOS"], True, False),
        (["XROS"], False, True),
    ),
)
def test_target_platform(
    create_ipa: Callable[[List[str]], Ipa],
    supported_platforms: List[str],
    expected_is_for_tvos: bool,
    expected_is_for_visionos: bool,
):
    ipa = create_ipa(supported_platforms)

    assert ipa.is_for_tvos() is expected_is_for_tvos
    assert ipa.is_for_visionos() is expected_is_for_visionos
