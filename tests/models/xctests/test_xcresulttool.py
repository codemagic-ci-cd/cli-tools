from typing import Optional
from unittest import mock

import pytest
from codemagic.models.xctests import XcResultTool
from packaging.version import Version


@pytest.mark.parametrize(
    ("xcresulttool_version", "expected_result"),
    (
        (None, False),
        (Version("0"), False),
        (Version("1"), False),
        (Version("23020.9"), False),
        (Version("23021"), True),
        (Version("23021.1"), True),
        (Version("23022"), True),
        (Version("33022"), True),
    ),
)
def test_requires_legacy_flag(xcresulttool_version: Optional[Version], expected_result: bool):
    with mock.patch.object(XcResultTool, "get_tool_version", new=mock.MagicMock(return_value=xcresulttool_version)):
        assert expected_result is XcResultTool._requires_legacy_flag()
