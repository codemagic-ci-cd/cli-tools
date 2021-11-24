import argparse
import os
import pathlib
from tempfile import NamedTemporaryFile
from typing import Any
from typing import Type
from typing import Union

import pytest

from codemagic import cli
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.cli.argument import EnvironmentArgumentValue
from codemagic.cli.argument import TypedCliArgument

mocks_dir = pathlib.Path(__file__).parent.parent / 'mocks'


class CustomStr(str):
    pass


def integer_converter(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f'{s} is not a valid integer')


class _TypedArgument(cli.TypedCliArgument[pathlib.Path]):
    environment_variable_key = '_TYPED_ARGUMENT_'
    argument_type = CustomStr


class _TestArgument(cli.Argument):
    TYPED_ARGUMENT = cli.ArgumentProperties(
        key='typed_argument',
        type=_TypedArgument,
        description='typed argument')
    PATH_ARGUMENT = cli.ArgumentProperties(
        key='path_argument',
        type=pathlib.Path,
        description='path')
    INT_ARGUMENT = cli.ArgumentProperties(
        key='int_argument',
        type=integer_converter,
        description='integer')


@pytest.mark.parametrize('file_contents', [
    'my secret value',
    'my secret value\n',
    '\nmy secret value\n',
    '( ͡° ͜ʖ ͡°)',
    '(╯°□°）╯︵ ┻━┻',
    mocks_dir / 'utf-8-sample.txt',
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


@pytest.mark.parametrize('argument', _TestArgument)
def test_raise_argument_error(argument: cli.Argument, cli_argument_group):
    argument.register(cli_argument_group)
    with pytest.raises(argparse.ArgumentError) as error_info:
        argument.raise_argument_error()

    error_msg = Colors.remove(str(error_info.value))
    key = argument.key
    assert error_msg.startswith(f'argument {key}: ')
    assert any([
        f'Value {key.upper()} not provided' in error_msg,
        f'Missing value {key.upper()}' in error_msg,
    ])


@pytest.mark.parametrize('argument', _TestArgument)
def test_raise_argument_error_custom_message(argument: cli.Argument, cli_argument_group):
    argument.register(cli_argument_group)
    with pytest.raises(argparse.ArgumentError) as error_info:
        argument.raise_argument_error('Custom error')

    error_msg = Colors.remove(str(error_info.value))
    assert error_msg == f'argument {argument.key}: Custom error'


@pytest.mark.parametrize('is_switched_on, is_switched_off', [
    (True, True),
    (False, False),
])
def test_exclusive_optional_arguments_exception(is_switched_on, is_switched_off):
    with pytest.raises(ValueError):
        Argument.resolve_optional_two_way_switch(is_switched_on, is_switched_off)


@pytest.mark.parametrize('is_switched_on, is_switched_off, expected_value', [
    (None, None, None),
    (None, False, None),
    (False, None, None),
    (True, None, True),
    (True, False, True),
    (False, True, False),
    (None, True, False),
])
def test_binary_arguments_value(is_switched_on, is_switched_off, expected_value):
    assert Argument.resolve_optional_two_way_switch(is_switched_on, is_switched_off) == expected_value


def test_with_custom_argument_group():
    argument_group_name = 'group_name'
    args_with_custom_group = tuple(cli.Argument.with_custom_argument_group(
        argument_group_name,
        _TestArgument.TYPED_ARGUMENT,
        _TestArgument.INT_ARGUMENT,
        exclude=[_TestArgument.TYPED_ARGUMENT],
    ))
    assert len(args_with_custom_group) == 1
    arg = args_with_custom_group[0]
    assert arg is not _TestArgument.INT_ARGUMENT
    assert arg.name == _TestArgument.INT_ARGUMENT.name
    assert arg.__class__.__name__ == _TestArgument.INT_ARGUMENT.__class__.__name__
    assert arg.value.argument_group_name == argument_group_name
    assert _TestArgument.INT_ARGUMENT.value.argument_group_name is None
    assert arg.value.key == _TestArgument.INT_ARGUMENT.key
    assert arg.value.description == _TestArgument.INT_ARGUMENT.description
    assert arg.value.type == _TestArgument.INT_ARGUMENT.type
    assert arg.value.flags == _TestArgument.INT_ARGUMENT.flags
    assert arg.value.argparse_kwargs == _TestArgument.INT_ARGUMENT.argparse_kwargs
