from __future__ import annotations

from codemagic_cli_tools.apple.resources import Device


def test_device_initialization(api_device):
    device = Device(api_device)
    assert device.dict() == api_device
