from unittest import mock

import pytest

from codemagic.utilities.decorators import run_once


def test_run_once():
    m = mock.MagicMock(side_effect=[1, 2, 3])

    @run_once
    def my_function():
        return m()

    assert my_function() == 1
    assert my_function() == 1
    assert my_function() == 1
    assert my_function() == 1
    m.assert_called_once()


def test_run_once_with_args():
    m = mock.MagicMock(side_effect=["a", "b", "c"])

    @run_once
    def my_function(a, b, *, c):
        return m(a, b, c=c)

    assert my_function(1, 2, c=3) == "a"
    assert my_function(4, 5, c=6) == "a"
    assert my_function(7, 8, c=9) == "a"
    m.assert_called_once_with(1, 2, c=3)


def test_run_once_with_exception():
    m = mock.MagicMock()

    @run_once
    def my_function(a, b):
        m(a, b)
        return a / b

    with pytest.raises(ZeroDivisionError):
        my_function(1, 0)

    assert my_function(1, 1) == 1
    assert my_function(1, 2) == 1
    assert my_function(1, 3) == 1
    assert m.call_count == 2
    m.assert_has_calls(
        [
            mock.call(1, 0),
            mock.call(1, 1),
        ],
    )
