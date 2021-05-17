import json
import pathlib
from typing import Any
from typing import Dict

import pytest

from codemagic.models.altool import AltoolResult


@pytest.fixture
def mock_validation_failure() -> Dict[str, Any]:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'mock_validation_failure.json'
    return json.loads(mock_path.read_text())


@pytest.fixture
def mock_upload_success() -> Dict[str, Any]:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'mock_upload_success.json'
    return json.loads(mock_path.read_text())


def test_upload_success_result(mock_upload_success):
    result = AltoolResult.create(**mock_upload_success)
    assert result.tool_version == '4.029.1194'
    assert result.tool_path == '/Applications/Xcode.app/Contents/.../AppStoreService.framework'
    assert result.success_message == "No errors uploading 'macos_example.pkg'"
    assert result.os_version == '11.2.3'


def test_validation_failure_result(mock_validation_failure):
    expected_error_message = (
        'Unable to process application at this time due to the following error: Invalid Provisioning Profile. '
        'The provisioning profile included in the bundle io.codemagic.banaan [Payload/banaan.app] is invalid. '
        '[Missing code-signing certificate]. '
        'A Distribution Provisioning profile should be used when submitting apps to the App Store. '
        'For more information, visit the iOS Developer Portal..'
    )
    result = AltoolResult.create(**mock_validation_failure)
    assert result.tool_version == '4.050.1210'
    assert result.tool_path == '/Applications/Xcode.app/Contents/.../AppStoreService.framework'
    assert result.os_version == '11.2.3'
    assert len(result.product_errors) == 1
    product_error = result.product_errors[0]
    assert product_error.message == expected_error_message
    assert product_error.code == 1176
    user_info = product_error.user_info
    assert user_info.failure_reason == 'App Store operation failed.'
    assert user_info.recovery_suggestion == expected_error_message
    assert user_info.description == expected_error_message
