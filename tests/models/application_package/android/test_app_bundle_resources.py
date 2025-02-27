import pathlib

import pytest

from codemagic.models.application_package.android import AppBundleResources


@pytest.fixture
def app_bundle_resources() -> AppBundleResources:
    mock_dump_path = pathlib.Path(__file__).parent / "mocks" / "bundle_resources_dump.txt"
    return AppBundleResources(mock_dump_path.read_text())


@pytest.mark.parametrize(
    ("label", "expected_resource_value"),
    (
        ("color/white", "#ffffffff"),  # l 66
        ("string/app_name", "CLI tools test app"),  # l378
        ("string/call_notification_answer_action", "Answer"),
        ("xml/backup_rules", "res/xml/backup_rules.xml"),  # l 7635
        ("styleable/GradientColorItem", "[@android:attr/offset, @android:attr/color]"),  # l 7633
    ),
)
def test_get_resources(label: str, expected_resource_value: str, app_bundle_resources: AppBundleResources):
    resource = app_bundle_resources.get_resource(label)
    assert resource == expected_resource_value


def test_get_resource_missing_value(app_bundle_resources: AppBundleResources):
    resource = app_bundle_resources.get_resource("label/not_defined")
    assert resource is None
