from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from codemagic_cli_tools.apple.resources import BundleId


@pytest.fixture
def api_bundle_id() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'bundle_id.json'
    return json.loads(mock_path.read_text())


def test_bundle_id_initialization(api_bundle_id):
    bundle_id = BundleId(api_bundle_id)
    assert bundle_id.dict() == api_bundle_id
