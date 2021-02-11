import pytest

from codemagic.utilities.argument_utils import get_binary_arguments_value


def test_binary_arguments_exclusive():
    with pytest.raises(Exception):
        get_binary_arguments_value(True, True)


@pytest.mark.parametrize('value, not_value, expected_value', [
    (None, None, None),
    (None, True, False),
    (True, None, True),
])
def test_binary_arguments_value(value, not_value, expected_value):
    assert get_binary_arguments_value(value, not_value) == expected_value
