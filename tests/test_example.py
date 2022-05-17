import pytest


@pytest.mark.skip(reason='This is a failing test')
def test_fail():
    assert False, 'This shall not pass'


def test_succeed():
    assert True, 'This shall pass'


@pytest.mark.skip(reason='Skip it')
def test_skip():
    pass  # Skipped
