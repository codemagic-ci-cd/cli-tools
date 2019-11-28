from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from apple.resources import Certificate


@pytest.fixture
def api_certificate() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'certificate.json'
    return json.loads(mock_path.read_text())


def test_certificate_initialization(api_certificate):
    certificate = Certificate(api_certificate)
    assert certificate.dict() == api_certificate
