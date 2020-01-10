from __future__ import annotations

from codemagic.apple.resources import Profile


def test_profile_initialization(api_profile):
    profile = Profile(api_profile)
    assert profile.dict() == api_profile
    assert profile.relationships.devices.data[0].id == '8UCFZA68RK'
