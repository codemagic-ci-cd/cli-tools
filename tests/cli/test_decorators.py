import argparse

import pytest

from codemagic import cli


class _TestArgument(cli.Argument):
    ARG1 = cli.ArgumentProperties(key='arg1', description='')
    ARG2 = cli.ArgumentProperties(key='arg2', description='')
    ARG3 = cli.ArgumentProperties(key='arg3', description='')
    ARG4 = cli.ArgumentProperties(key='arg4', description='')


def test_class_arguments_inclusion():
    @cli.common_arguments(_TestArgument.ARG1, _TestArgument.ARG2)
    class BaseCliApp(cli.CliApp):
        def __init__(self, arg1, arg2, **kwargs):
            super().__init__(**kwargs)
            self.arg1 = arg1
            self.arg2 = arg2

    @cli.common_arguments(_TestArgument.ARG3, _TestArgument.ARG4)
    class MyApp(BaseCliApp):
        def __init__(self, arg3, arg4, **kwargs):
            super().__init__(**kwargs)
            self.arg3 = arg3
            self.arg4 = arg4

    cli_args = argparse.Namespace(**{arg.key: f'{arg.key}-value' for arg in _TestArgument})
    cli_app = MyApp.from_cli_args(cli_args)
    assert cli_app.arg1 == 'arg1-value'
    assert cli_app.arg2 == 'arg2-value'
    assert cli_app.arg3 == 'arg3-value'
    assert cli_app.arg4 == 'arg4-value'


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
