import json
import pathlib
from types import SimpleNamespace
from unittest import mock

import pytest

from codemagic.models import Altool
from codemagic.models.altool import AltoolResult
from codemagic.models.altool.altool import AltoolCommandError
from codemagic.models.altool.altool import PlatformType


@pytest.fixture
def mock_altool():
    Altool._ensure_altool = mock.Mock(return_value=True)
    altool = Altool(
        username='user@example.com',
        password='xxxx-yyyy-zzzz-wwww',
    )
    mock_echo = mock.MagicMock()
    altool._kill_xcode_processes_for_retrying = mock.Mock()
    altool.get_current_cli_app = lambda: SimpleNamespace(echo=mock_echo)
    return altool


@pytest.fixture
def mock_success_result():
    return AltoolResult.create(**{
        'tool-version': '4.050.1210',
        'tool-path': '/Applications/Xcode.app/Contents/.../AppStoreService.framework',
        'os-version': '11.2.3',
    })


@pytest.fixture
def mock_other_error_stdout() -> str:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'mock_failure_other.txt'
    return mock_path.read_text()


@pytest.fixture
def mock_auth_error_stdout() -> str:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'mock_failure_auth.txt'
    return mock_path.read_text()


@pytest.fixture
def mock_success_stdout() -> str:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'mock_upload_success.json'
    return mock_path.read_text()


@mock.patch.object(PlatformType, 'from_path', lambda _artifact_path: PlatformType.IOS)
@pytest.mark.parametrize('retries, error_message', [
    (2, 'error'),
    (5, 'another error'),
    (15, 'also error'),
])
def test_retrying_command_exhaustion(mock_altool, mock_auth_error_stdout, retries, error_message):
    raise_error = mock.Mock(side_effect=AltoolCommandError(error_message, mock_auth_error_stdout))
    with mock.patch.object(mock_altool, '_run_command', side_effect=raise_error):
        with pytest.raises(IOError) as error_info:
            mock_altool.upload_app(pathlib.Path('app.ipa'), retries=retries, retry_wait_seconds=0)
    assert str(error_info.value) == error_message
    mock_echo: mock.Mock = mock_altool.get_current_cli_app().echo  # type: ignore
    assert mock_echo.call_count == retries + 1  # One for each retry, and final stdout logging
    final_echo_call = mock_echo.call_args_list[-1]
    assert final_echo_call[0][0] == json.dumps(json.loads(mock_auth_error_stdout), indent=4)
    mock_kill_xcodes: mock.Mock = mock_altool._kill_xcode_processes_for_retrying  # type: ignore
    mock_kill_xcodes.assert_called()


@mock.patch.object(PlatformType, 'from_path', lambda _artifact_path: PlatformType.IOS)
def test_no_retries(mock_altool, mock_auth_error_stdout):
    raise_error = mock.Mock(side_effect=AltoolCommandError('my error', mock_auth_error_stdout))
    with mock.patch.object(mock_altool, '_run_command', side_effect=raise_error):
        with pytest.raises(IOError) as error_info:
            mock_altool.upload_app(pathlib.Path('app.ipa'), retries=1, retry_wait_seconds=0)
    assert str(error_info.value) == 'my error'
    mock_echo: mock.Mock = mock_altool.get_current_cli_app().echo  # type: ignore
    assert mock_echo.call_count == 1  # One for each retry, and final stdout logging
    final_echo_call = mock_echo.call_args_list[-1]
    assert final_echo_call[0][0] == json.dumps(json.loads(mock_auth_error_stdout), indent=4)


@mock.patch.object(PlatformType, 'from_path', lambda _artifact_path: PlatformType.IOS)
def test_retrying_command_failure(mock_altool, mock_auth_error_stdout, mock_other_error_stdout):
    raise_errors = mock.Mock(side_effect=(
        AltoolCommandError('my error', mock_auth_error_stdout),
        AltoolCommandError('my error', mock_auth_error_stdout),
        AltoolCommandError('this shall not pass', mock_other_error_stdout),
    ))
    with mock.patch.object(mock_altool, '_run_command', side_effect=raise_errors):
        with pytest.raises(IOError) as error_info:
            mock_altool.upload_app(pathlib.Path('app.ipa'), retries=100, retry_wait_seconds=0)

    assert str(error_info.value) == 'this shall not pass'
    mock_echo: mock.Mock = mock_altool.get_current_cli_app().echo  # type: ignore
    expected_outputs = (
        'Failed to upload archive, but this might be a temporary issue, retrying...',
        'Attempt #2 to upload failed, retrying...',
        'Attempt #3 to upload failed.',
        json.dumps(json.loads(mock_other_error_stdout), indent=4),
    )
    for call, expected_output in zip(mock_echo.call_args_list, expected_outputs):
        assert call[0][0] == expected_output
    mock_kill_xcodes: mock.Mock = mock_altool._kill_xcode_processes_for_retrying  # type: ignore
    assert mock_kill_xcodes.call_count == 2


@mock.patch.object(PlatformType, 'from_path', lambda _artifact_path: PlatformType.IOS)
def test_retrying_command_success(mock_altool, mock_auth_error_stdout, mock_success_result):
    raise_errors = mock.Mock(side_effect=(
        AltoolCommandError('my error', mock_auth_error_stdout),
        AltoolCommandError('my error', mock_auth_error_stdout),
        mock_success_result,
    ))
    with mock.patch.object(mock_altool, '_run_command', side_effect=raise_errors):
        result = mock_altool.upload_app(pathlib.Path('app.ipa'), retries=100, retry_wait_seconds=0)

    assert result is mock_success_result
    mock_echo: mock.Mock = mock_altool.get_current_cli_app().echo  # type: ignore
    assert mock_echo.call_count == 2
    expected_outputs = (
        'Failed to upload archive, but this might be a temporary issue, retrying...',
        'Attempt #2 to upload failed, retrying...',
    )
    for call, expected_output in zip(mock_echo.call_args_list, expected_outputs):
        assert call[0][0] == expected_output
    mock_kill_xcodes: mock.Mock = mock_altool._kill_xcode_processes_for_retrying  # type: ignore
    assert mock_kill_xcodes.call_count == 2


@mock.patch.object(PlatformType, 'from_path', lambda _artifact_path: PlatformType.IOS)
def test_retrying_command_immediate_success(mock_altool, mock_success_stdout, mock_success_result):
    with mock.patch.object(mock_altool, '_run_command', side_effect=[mock_success_result]):
        result = mock_altool.upload_app(pathlib.Path('app.ipa'), retries=100, retry_wait_seconds=0)
    assert result is mock_success_result
