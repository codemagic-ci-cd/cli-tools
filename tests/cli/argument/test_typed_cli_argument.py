import argparse
import contextlib
import os
import pathlib
from unittest import mock

import pytest

from codemagic.cli.argument.typed_cli_argument import EnvironmentArgumentValue
from codemagic.cli.argument.typed_cli_argument import TypedCliArgument


@contextlib.contextmanager
def environment_variable_value(name: str, value: str):
    current_value = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        os.environ.pop(name)
        if current_value is not None:
            os.environ[name] = current_value


def test_deprecated_environment_variable_key_without_replacement():
    with pytest.raises(ValueError):

        class MyTypedArgument(TypedCliArgument[str]):
            deprecated_environment_variable_key = "DEPRECATED_ENVIRONMENT_VARIABLE_KEY"


@pytest.mark.parametrize(
    "environment_variable_key",
    ("ENVIRONMENT_VARIABLE_KEY", "DEPRECATED_ENVIRONMENT_VARIABLE_KEY"),
)
def test_deprecated_environment_variable_key(environment_variable_key):
    class MyTypedArgument(TypedCliArgument[str]):
        environment_variable_key = "ENVIRONMENT_VARIABLE_KEY"
        deprecated_environment_variable_key = "DEPRECATED_ENVIRONMENT_VARIABLE_KEY"

    with environment_variable_value(environment_variable_key, "value from environment variable"):
        my_typed_argument = MyTypedArgument.from_environment_variable_default()

    assert my_typed_argument.value == "value from environment variable"


@mock.patch("codemagic.cli.argument.typed_cli_argument.Path", spec=pathlib.Path)
def test_value_from_file_with_environment_variables(mock_path: mock.MagicMock):
    class MyEnvironmentArgumentValue(EnvironmentArgumentValue[str]):
        pass

    path = mock_path.return_value
    path.expanduser.return_value = path
    path.exists.return_value = True
    path.is_file.return_value = True
    path.read_text.return_value = "value from file with environment variables"

    with (
        environment_variable_value("DIRPATH", "/path/to"),
        environment_variable_value("FILENAME", "filename.txt"),
    ):
        argument_value = MyEnvironmentArgumentValue("@file:$DIRPATH/$FILENAME")

    assert argument_value.value == "value from file with environment variables"
    mock_path.assert_called_once_with("/path/to/filename.txt")


@mock.patch("codemagic.cli.argument.typed_cli_argument.Path", spec=pathlib.Path)
def test_value_from_file_with_tilde_path(mock_path: mock.MagicMock):
    class MyEnvironmentArgumentValue(EnvironmentArgumentValue[str]):
        pass

    resolved_path = pathlib.Path(os.path.expandvars("$HOME/path/to/filename.txt"))
    path = mock_path.return_value
    path.expanduser.return_value = resolved_path

    with pytest.raises(argparse.ArgumentTypeError) as error_info:
        MyEnvironmentArgumentValue("@file:~/path/to/filename.txt")

    assert error_info.value.args[0] == f'File "{resolved_path}" does not exist'
    mock_path.assert_called_once_with("~/path/to/filename.txt")
