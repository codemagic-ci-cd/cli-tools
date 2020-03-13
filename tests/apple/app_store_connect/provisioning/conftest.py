import json
import pathlib
from typing import Dict

import pytest


_RESOURCE_MOCKS_DIR = pathlib.Path(__file__).parent.parent.parent / 'resources' / 'mocks'


@pytest.fixture
def profile_response() -> Dict:
    mock_path = _RESOURCE_MOCKS_DIR / 'profile.json'
    return {'data': json.loads(mock_path.read_text())}
