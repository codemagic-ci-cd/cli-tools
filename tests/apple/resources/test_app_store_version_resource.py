from __future__ import annotations

from codemagic.apple.resources import AppStoreVersion


def test_app_store_version_initialization(api_app_store_version: dict):
    app_store_version = AppStoreVersion(api_app_store_version)
    assert app_store_version.dict() == api_app_store_version
