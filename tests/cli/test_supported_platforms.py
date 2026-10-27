import inspect

import pytest

import codemagic.tools
from codemagic import cli
from codemagic.cli import Platform


def _tool_classes():
    return [
        tool
        for _, tool in inspect.getmembers(codemagic.tools, inspect.isclass)
        if issubclass(tool, cli.CliApp) and tool is not cli.CliApp
    ]


@pytest.mark.parametrize("tool", _tool_classes(), ids=lambda tool: tool.get_executable_name())
def test_tool_declares_supported_platforms(tool):
    assert tool.SUPPORTED_PLATFORMS, f"{tool.__name__} must declare SUPPORTED_PLATFORMS"
    assert all(isinstance(supported, Platform) for supported in tool.SUPPORTED_PLATFORMS)


def test_description_appends_the_supported_platforms():
    assert codemagic.tools.CodemagicCliTools.get_description().endswith(
        "\nPlatform support: Linux, macOS and Windows.",
    )
    assert codemagic.tools.Keychain.get_description().endswith("\nPlatform support: macOS.")
