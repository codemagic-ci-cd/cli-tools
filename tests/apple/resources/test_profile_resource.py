from __future__ import annotations

import pytest

from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState


def test_profile_initialization(api_profile):
    profile = Profile(api_profile)
    assert profile.dict() == api_profile
    assert profile.relationships.devices.data[0].id == "8UCFZA68RK"
    assert profile.has_profile_content is True


def test_profile_without_content(api_profile_without_content):
    profile = Profile(api_profile_without_content)
    assert profile.attributes.profileContent is None
    assert profile.has_profile_content is False
    assert profile.attributes.profileState is ProfileState.EXPIRED
    assert profile.attributes.profileVersion == "1"
    assert profile.dict()["attributes"].keys() == api_profile_without_content["attributes"].keys()
    with pytest.raises(ValueError, match="does not have profile content"):
        _ = profile.profile_content


def test_profile_with_empty_content(api_profile):
    api_profile["attributes"]["profileContent"] = ""
    profile = Profile(api_profile)
    assert profile.has_profile_content is False
    with pytest.raises(ValueError, match="does not have profile content"):
        _ = profile.profile_content
