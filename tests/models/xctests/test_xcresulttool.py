from typing import Optional
from unittest import mock

import pytest
from codemagic.models.xctests import XcResultTool
from packaging.version import Version


@pytest.mark.parametrize(
    ("xcresulttool_version", "expected_result"),
    (
        (None, False),
        (Version("0"), True),
        (Version("1"), True),
        (Version("23020.9"), True),
        (Version("23021"), False),
        (Version("23021.1"), False),
        (Version("23022"), False),
        (Version("33022"), False),
    ),
)
def test_is_legacy(xcresulttool_version: Optional[Version], expected_result: bool):
    with mock.patch.object(XcResultTool, "get_tool_version", new=mock.MagicMock(return_value=xcresulttool_version)):
        assert expected_result is XcResultTool.is_legacy()
