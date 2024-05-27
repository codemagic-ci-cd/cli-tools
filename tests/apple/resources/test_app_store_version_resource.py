from __future__ import annotations

from codemagic.apple.resources import AppStoreVersion


def test_app_store_version_initialization(api_app_store_version):
    app_store_version = AppStoreVersion(api_app_store_version)
    assert app_store_version.dict() == api_app_store_version


def test_app_store_version_without_idfa_declaration(api_app_store_version):
    api_relationships = api_app_store_version["relationships"]
    del api_relationships["idfaDeclaration"]
    app_store_version = AppStoreVersion(api_app_store_version)
    assert app_store_version.dict() == api_app_store_version
