from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from codemagic_cli_tools.apple.resources import Device


@pytest.fixture
def api_device() -> Dict:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'device.json'
    return json.loads(mock_path.read_text())


def test_device_initialization(api_device):
    device = Device(api_device)
    assert device.dict() == api_device
