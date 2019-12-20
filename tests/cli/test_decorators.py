import pytest

from codemagic_cli_tools import cli


class _TestArgument(cli.Argument):
    ARG1 = cli.ArgumentProperties(key='arg1', description='')
    ARG2 = cli.ArgumentProperties(key='arg2', description='')
    ARG3 = cli.ArgumentProperties(key='arg3', description='')
    ARG4 = cli.ArgumentProperties(key='arg4', description='')


def test_class_arguments_inheritance():
    @cli.common_arguments(_TestArgument.ARG1, _TestArgument.ARG2)
    class BaseCliApp(cli.CliApp):
        ...

    @cli.common_arguments(_TestArgument.ARG3, _TestArgument.ARG4)
    class CliApp(BaseCliApp):
        ...

    for argument in _TestArgument:
        assert argument in CliApp.CLASS_ARGUMENTS


def test_class_arguments_duplicates():
    with pytest.raises(ValueError):
        @cli.common_arguments(_TestArgument.ARG1, _TestArgument.ARG1)
        class CliApp(cli.CliApp):
            ...


def test_class_arguments_duplicates_on_inheritance():
    @cli.common_arguments(_TestArgument.ARG1)
    class BaseCliApp(cli.CliApp):
        ...

    with pytest.raises(ValueError):
        @cli.common_arguments(_TestArgument.ARG1)
        class CliApp(BaseCliApp):
            ...


def test_invalid_class_argument():
    with pytest.raises(TypeError):
        @cli.common_arguments('ARGUMENT')
        class CliApp(cli.CliApp):
            ...
