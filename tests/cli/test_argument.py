import argparse
import os
import pathlib
from tempfile import NamedTemporaryFile
from typing import Any
from typing import Type
from typing import Union

import pytest

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli.argument import EnvironmentArgumentValue
from codemagic_cli_tools.cli.argument import TypedCliArgument

mock_dir = pathlib.Path(__file__).parent / 'mocks'


class CustomStr(str):
    pass


class _TypedArgument(cli.TypedCliArgument[pathlib.Path]):
    environment_variable_key = '_TYPED_ARGUMENT_'
    argument_type = CustomStr


class _TestArgument(cli.Argument):
    TYPED_ARGUMENT = cli.ArgumentProperties(key='typed_argument', type=_TypedArgument, description='')


@pytest.mark.parametrize('file_contents', [
    'my secret value',
    'my secret value\n',
    '\nmy secret value\n',
    '( ͡° ͜ʖ ͡°)',
    '(╯°□°）╯︵ ┻━┻',
    mock_dir / 'utf-8-sample.txt',
])
def test_environment_argument_value_from_file(file_contents: Union[pathlib.Path, str]):
    if isinstance(file_contents, pathlib.Path):
        file_contents = file_contents.read_text()
    actual_value = file_contents
    with NamedTemporaryFile(mode='w') as tf:
        tf.write(actual_value)
        tf.flush()
        argument_value = EnvironmentArgumentValue(f'@file:{tf.name}')
    assert argument_value.value == actual_value


def test_environment_argument_value_from_environment():
    actual_value = 'my secret value'
    key = 'MY_SECRET'
    os.environ[key] = actual_value
    argument_value = EnvironmentArgumentValue(f'@env:{key}')
    assert argument_value.value == actual_value


def test_environment_argument_value_verbatim():
    actual_value = 'my public value'
    argument_value = EnvironmentArgumentValue(actual_value)
    assert argument_value.value == actual_value


@pytest.mark.parametrize('given_type, raw_input, expected_value', [
    (int, '111', 111),
    (float, '1.5', 1.5),
    (list, 'abc', ['a', 'b', 'c']),
    (tuple, '12', ('1', '2')),
    (CustomStr, 'my_str', CustomStr('my_str')),
    (str, 'my_str', 'my_str'),
])
def test_environment_argument_value_custom_type(
        given_type: Type, raw_input: str, expected_value: Any):
    class CustomTypeEnvVar(EnvironmentArgumentValue[given_type]):
        argument_type = given_type

    argument_value = CustomTypeEnvVar(raw_input)
    assert isinstance(argument_value.value, given_type)
    assert argument_value.value == expected_value


@pytest.mark.parametrize('env_var_key, given_type, raw_input, expected_value', [
    ('INT_KEY', int, '111', 111),
    ('FLOAT_KEY', float, '1.5', 1.5),
    ('LIST_KEY', list, 'abc', ['a', 'b', 'c']),
    ('TUPLE_KEY', tuple, '12', ('1', '2')),
    ('CUSTOM_STR_KEY', CustomStr, 'my_str', CustomStr('my_str')),
    ('STR_KEY', str, 'my_str', 'my_str'),
])
def test_environment_variable_fallback(
        env_var_key: str, given_type: Type, raw_input: str, expected_value: Any):
    class EnvVarDefaultType(TypedCliArgument[given_type]):
        environment_variable_key = env_var_key
        argument_type = given_type

    os.environ[env_var_key] = raw_input
    argument_value = EnvVarDefaultType.from_environment_variable_default()
    assert argument_value.value == expected_value


def test_typed_cli_argument_initialization_with_value_from_cli():
    value = _TypedArgument('some_value')
    parsed_value = _TestArgument.TYPED_ARGUMENT.from_args(argparse.Namespace(typed_argument=value))
    assert parsed_value.value == value.value
    assert isinstance(parsed_value.value, CustomStr)
    assert str(parsed_value) == value.value


def test_typed_cli_argument_initialization_with_no_value():
    parsed_value = _TestArgument.TYPED_ARGUMENT.from_args(argparse.Namespace(typed_argument=None))
    assert parsed_value is None


def test_typed_cli_argument_initialization_with_value_from_env():
    value = _TypedArgument('some_value')
    os.environ[value.environment_variable_key] = value.value
    parsed_value = _TestArgument.TYPED_ARGUMENT.from_args(argparse.Namespace(typed_argument=None))
    assert parsed_value.value == value.value
    assert isinstance(parsed_value.value, CustomStr)
    assert str(parsed_value) == f'@env:{value.environment_variable_key}'
