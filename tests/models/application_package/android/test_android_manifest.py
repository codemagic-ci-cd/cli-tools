import pathlib

import pytest

from codemagic.models.application_package.android import AndroidManifest


@pytest.fixture
def android_manifest() -> AndroidManifest:
    mock_manifest_path = pathlib.Path(__file__).parent / "mocks" / "AndroidManifest.xml"
    return AndroidManifest(mock_manifest_path.read_text())


def test_version_name(android_manifest: AndroidManifest):
    assert android_manifest.version_name == "3.14"


def test_version_code(android_manifest: AndroidManifest):
    assert android_manifest.version_code == "8"


def test_app_label(android_manifest: AndroidManifest):
    assert android_manifest.app_label == "@string/app_name"


def test_package_name(android_manifest: AndroidManifest):
    assert android_manifest.package_name == "io.codemagic.cli_tools"


def test_min_sdk_version(android_manifest: AndroidManifest):
    assert android_manifest.min_sdk_version == "24"


def test_target_sdk_version(android_manifest: AndroidManifest):
    assert android_manifest.target_sdk_version == "35"


def test_debuggable(android_manifest: AndroidManifest):
    assert android_manifest.debuggable == ""
