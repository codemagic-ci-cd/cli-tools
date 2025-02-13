from unittest import mock

import pytest
from packaging.version import Version

from codemagic.models.xctests import XcResultTool


@pytest.mark.parametrize(
    "xcode_version",
    ("1", "10", "14.4", "15.0", "15.1", "15.2", "15.3", "15.4", "15.9.10"),
)
def test_is_legacy(xcode_version: str):
    mock_xcode = mock.MagicMock(version=Version(xcode_version))
    with mock.patch.object(XcResultTool, "_get_selected_xcode", new=mock.MagicMock(return_value=mock_xcode)):
        assert XcResultTool.is_legacy() is True


@pytest.mark.parametrize(
    "xcode_version",
    ("16", "16.0", "16.0.1", "16.0.0", "16.1", "16.2", "17.2", "20.2", "100"),
)
def test_is_not_legacy(xcode_version: str):
    mock_xcode = mock.MagicMock(version=Version(xcode_version))
    with mock.patch.object(XcResultTool, "_get_selected_xcode", new=mock.MagicMock(return_value=mock_xcode)):
        assert XcResultTool.is_legacy() is False
