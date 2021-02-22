from __future__ import annotations

from codemagic.apple.resources import AppStoreVersion


def test_build_initialization(api_app_store_version):
    app_store_version = AppStoreVersion(api_app_store_version)
    assert app_store_version.dict() == api_app_store_version
