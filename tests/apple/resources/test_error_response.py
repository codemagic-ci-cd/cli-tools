from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from codemagic_cli_tools.apple.resources import ErrorResponse


@pytest.fixture
def api_error_response() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'error_response.json'
    return json.loads(mock_path.read_text())


def test_error_response_initialization(api_error_response):
    error_response = ErrorResponse(api_error_response)
    assert error_response.dict() == api_error_response
