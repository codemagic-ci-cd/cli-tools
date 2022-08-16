import pathlib

import pytest


@pytest.fixture
def mock_keystore_path():
    return pathlib.Path(__file__).parent / 'mocks' / 'android.ks'
