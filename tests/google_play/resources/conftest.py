import json
import pathlib
from typing import Dict

import pytest


@pytest.fixture
def api_edit() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'edit.json'
    return json.loads(mock_path.read_text())


@pytest.fixture
def api_track() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'track.json'
    return json.loads(mock_path.read_text())
