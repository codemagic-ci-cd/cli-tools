import json
import pathlib

import pytest

_RESOURCE_MOCKS_DIR = pathlib.Path(__file__).parent.parent.parent / 'resources' / 'mocks'


class MockResponse:
    def __init__(self, mock_data):
        self.data = {'data': mock_data}

    def json(self):
        return self.data


@pytest.fixture
def profile_response() -> MockResponse:
    mock_path = _RESOURCE_MOCKS_DIR / 'profile.json'
    mock_data = json.loads(mock_path.read_text())
    return MockResponse(mock_data)
