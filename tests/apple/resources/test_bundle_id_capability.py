from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from apple.resources import BundleIdCapability


@pytest.fixture
def api_bundle_id_capability() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'bundle_id_capability.json'
    return json.loads(mock_path.read_text())


def test_app_initialization(api_bundle_id_capability):
    bundle_id_capability = BundleIdCapability(api_bundle_id_capability)
    assert bundle_id_capability.dict() == api_bundle_id_capability
