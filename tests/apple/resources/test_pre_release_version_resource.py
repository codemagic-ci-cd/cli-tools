from __future__ import annotations

from codemagic.apple.resources import PreReleaseVersion


def test_build_initialization(api_pre_release_version):
    pre_release_version = PreReleaseVersion(api_pre_release_version)
    assert pre_release_version.dict() == api_pre_release_version
