import pathlib
from pathlib import Path
from unittest import mock

import pytest

from codemagic.models import Altool
from codemagic.models.altool.enums import PlatformType


@pytest.fixture
def mocks_dir() -> pathlib.Path:
    return Path(__file__).parent / "mocks"


@mock.patch.object(PlatformType, "from_path", mock.Mock(return_value=PlatformType.IOS))
@mock.patch.object(Altool, "_ensure_altool", mock.Mock(return_value=True))
@mock.patch.object(Altool, "_log_process_output", mock.Mock())
@mock.patch("subprocess.check_output", autospec=True)
def test_error_handling_on_successful_returncode(mock_check_output: mock.Mock, mocks_dir: pathlib.Path):
    mock_check_output.side_effect = [(mocks_dir / "mock_upload_failed_stdout_xcode_26_0.txt").read_bytes()]

    altool = Altool(username="user@example.com", password="xxxx-yyyy-zzzz-wwww")
    with pytest.raises(IOError) as exc_info:
        altool.upload_app(Path("app.ipa"))

    mock_check_output.assert_called_once()
    assert exc_info.value.args == ('Failed to upload archive at "app.ipa":\nFailed to upload part number 8.',)


@pytest.mark.parametrize(
    "mock_name",
    [
        "mock_upload_success_stdout_xcode_16_4.txt",
        "mock_upload_success_stdout_xcode_26_0.txt",
        "mock_upload_success_verbose_stdout_xcode_15_4.txt",
        "mock_upload_success_verbose_stdout_xcode_16_4.txt",
        "mock_upload_success_verbose_stdout_xcode_26_0.txt",
        "mock_upload_failed_stdout_xcode_26_0.txt",
        "mock_upload_failed_stdout_xcode_16_4.txt",
        "mock_upload_failed_stdout_xcode_15_4.txt",
    ],
)
def test_parse_altool_result(mock_name: str, mocks_dir: pathlib.Path):
    altool_output = (mocks_dir / mock_name).read_text()
    result = Altool.parse_altool_result(altool_output)
    assert result is not None
