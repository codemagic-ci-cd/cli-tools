from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from apple.resources import App


@pytest.fixture
def api_app() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'app.json'
    return json.loads(mock_path.read_text())


def test_app_initialization(api_app):
    app = App(api_app)
    assert app.dict() == api_app
