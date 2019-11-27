import unittest

import pytest

from apple.app_store_connect_api import AppStoreConnectApiError
from apple.resources import BundleIdCapability
from apple.resources import CapabilityType
from apple.resources import ResourceId
from apple.resources import ResourceType

CAPYBARA_ID = ResourceId('F88J43FA9J')


@pytest.mark.skip(reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_api_client', 'class_logger')
class AppEndpointsTest(unittest.TestCase):

    def test_enable_capability(self):
        capability_type = CapabilityType.ACCESS_WIFI_INFORMATION
        capability = self.api_client.enable_capability(capability_type, CAPYBARA_ID)
        assert isinstance(capability, BundleIdCapability)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
        assert capability.attributes.capabilityType is capability_type

    def test_disable_capability(self):
        capability_id = ResourceId('F88J43FA9J_ACCESS_WIFI_INFORMATION')
        self.api_client.disable_capability(capability_id)

    def test_disable_capability_does_not_exist(self):
        with pytest.raises(AppStoreConnectApiError) as api_error:
            self.api_client.disable_capability(CapabilityType.DATA_PROTECTION)
        error = api_error.value.error_response.errors[0]
        assert error.code == 'NOT_FOUND'
        assert error.status == '404'

    def test_modify_capability_configuration(self):
        capability = self.api_client.modify_capability_configuration(
            ResourceId('F88J43FA9J_GAME_CENTER_IOS'),
            CapabilityType.GAME_CENTER,
            None
        )
        assert isinstance(capability, BundleIdCapability)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
