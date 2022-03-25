import pathlib

import pytest


@pytest.fixture
def _shell_tools_mocks_dir():
    return pathlib.Path(__file__).parent / 'mocks'


@pytest.fixture
def mock_keystore_path(_shell_tools_mocks_dir):
    return _shell_tools_mocks_dir / 'android.ks'
