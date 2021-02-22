from __future__ import annotations

from codemagic.apple.resources import Build


def test_build_initialization(api_build):
    build = Build(api_build)
    assert build.dict() == api_build
