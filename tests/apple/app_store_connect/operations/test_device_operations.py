import uuid

import pytest

from codemagic_cli_tools.apple.resources import BundleIdPlatform
from codemagic_cli_tools.apple.resources import Device
from codemagic_cli_tools.apple.resources import DeviceStatus
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase

DEVICE_ID = ResourceId('D9PW3SW6K2')
DEVICE_UDID = '5d0d1e9e3e4c8323756ec0038564006dafe15c21'


@pytest.mark.skip(reason='Live App Store Connect API access')
class DeviceOperationsTest(OperationsTestsBase):

    def test_register(self):
        device = self.api_client.devices.register(
            f'test device from {self.__class__.__name__}',
            BundleIdPlatform.IOS,
            DEVICE_UDID
        )
        assert isinstance(device, Device)

    def test_list(self):
        devices = self.api_client.devices.list()
        assert len(devices) > 0
        for device in devices:
            assert isinstance(device, Device)
            assert device.type is ResourceType.DEVICES

    def test_read(self):
        device_id = ResourceId('D9PW3SW6K2')
        device = self.api_client.devices.read(device_id)
        assert isinstance(device, Device)
        assert device.type is ResourceType.DEVICES

    def test_modify(self):
        new_name = f'test device {uuid.uuid4()}'
        new_status = DeviceStatus.DISABLED
        device = self.api_client.devices.modify(DEVICE_ID, name=new_name, status=new_status)
        assert isinstance(device, Device)
        assert device.attributes.name == new_name
        assert device.attributes.status is new_status
