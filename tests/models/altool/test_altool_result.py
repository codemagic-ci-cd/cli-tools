import json
import pathlib

import pytest

from codemagic.models.altool import AltoolResult
from codemagic.models.altool.altool_result import DeliveryDetails
from codemagic.models.altool.altool_result import UserInfo


@pytest.mark.parametrize(
    "mock_name",
    [
        "mock_upload_success_legacy.json",
        "mock_upload_success_xcode_16.json",
        "mock_upload_success_xcode_26.json",
    ],
)
def test_upload_success_result(mock_name: str):
    mock_path = pathlib.Path(__file__).parent / "mocks" / mock_name
    success_result_data = json.loads(mock_path.read_text())
    result = AltoolResult.create(**success_result_data)

    assert isinstance(result.tool_version, str) and result.tool_version
    assert isinstance(result.tool_path, str) and result.tool_path
    assert isinstance(result.success_message, str) and result.success_message
    assert isinstance(result.os_version, str) and result.os_version

    assert isinstance(result.details, (type(None), DeliveryDetails))
    assert result.product_errors == []
    assert result.warnings == []


@pytest.mark.parametrize(
    "mock_name",
    [
        "mock_upload_failure_legacy.json",
        "mock_upload_failure_xcode_16.json",
        "mock_upload_failure_xcode_26.json",
    ],
)
def test_upload_failure_result(mock_name: str):
    mock_path = pathlib.Path(__file__).parent / "mocks" / mock_name
    failure_result_data = json.loads(mock_path.read_text())
    result = AltoolResult.create(**failure_result_data)

    assert isinstance(result.tool_version, str) and result.tool_version
    assert isinstance(result.tool_path, str) and result.tool_path
    assert isinstance(result.success_message, str) and not result.success_message
    assert isinstance(result.os_version, str) and result.os_version

    assert result.details is None
    assert result.warnings == []
    assert len(result.product_errors) == 1

    product_error = result.product_errors[0]
    assert isinstance(product_error.user_info, UserInfo)


def test_validation_failure_result():
    mock_path = pathlib.Path(__file__).parent / "mocks" / "mock_validation_failure.json"
    validation_result_data = json.loads(mock_path.read_text())

    expected_error_message = (
        "Unable to process application at this time due to the following error: Invalid Provisioning Profile. "
        "The provisioning profile included in the bundle io.codemagic.banaan [Payload/banaan.app] is invalid. "
        "[Missing code-signing certificate]. "
        "A Distribution Provisioning profile should be used when submitting apps to the App Store. "
        "For more information, visit the iOS Developer Portal.."
    )
    result = AltoolResult.create(**validation_result_data)
    assert result.tool_version == "4.050.1210"
    assert result.tool_path == "/Applications/Xcode.app/Contents/.../AppStoreService.framework"
    assert result.os_version == "11.2.3"
    assert len(result.product_errors) == 1
    product_error = result.product_errors[0]
    assert product_error.message == expected_error_message
    assert product_error.code == 1176
    user_info = product_error.user_info
    assert user_info.failure_reason == "App Store operation failed."
    assert user_info.recovery_suggestion == expected_error_message
    assert user_info.description == expected_error_message
