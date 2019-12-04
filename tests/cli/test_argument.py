import os
import pathlib
from tempfile import NamedTemporaryFile
from typing import Type, Any, Union

import pytest

from codemagic_cli_tools.cli.argument import EnvironmentArgumentValue

mock_dir = pathlib.Path(__file__).parent / 'mocks'


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


class CustomStr(str):
    pass


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
