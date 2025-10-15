from pathlib import Path
from unittest import mock

import pytest

from codemagic.models import Altool
from codemagic.models.altool.enums import PlatformType


@mock.patch.object(PlatformType, "from_path", mock.Mock(return_value=PlatformType.IOS))
@mock.patch.object(Altool, "_ensure_altool", mock.Mock(return_value=True))
@mock.patch.object(Altool, "_log_process_output", mock.Mock())
@mock.patch("subprocess.check_output", autospec=True)
def test_error_handling_on_successful_returncode(mock_check_output: mock.Mock):
    mock_check_output.side_effect = [(Path(__file__).parent / "mocks" / "mock_upload_failed_stdout.txt").read_bytes()]

    altool = Altool(username="user@example.com", password="xxxx-yyyy-zzzz-wwww")
    with pytest.raises(IOError) as exc_info:
        altool.upload_app(Path("app.ipa"))

    mock_check_output.assert_called_once()
    assert exc_info.value.args == ('Failed to upload archive at "app.ipa":\nFailed to upload part number 8.',)
