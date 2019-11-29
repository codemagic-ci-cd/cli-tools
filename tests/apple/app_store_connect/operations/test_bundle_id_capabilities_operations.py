import pytest

from apple.app_store_connect import AppStoreConnectApiError
from apple.resources import BundleIdCapability
from apple.resources import CapabilityType
from apple.resources import ResourceId
from apple.resources import ResourceType
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase

CAPYBARA_ID = ResourceId('F88J43FA9J')


@pytest.mark.skip(reason='Live App Store Connect API access')
class BundleIdCapabilitiesOperationsTest(OperationsTestsBase):

    def test_enable_capability(self):
        capability_type = CapabilityType.ACCESS_WIFI_INFORMATION
        capability = self.api_client.bundle_id_capabilities.enable(capability_type, CAPYBARA_ID)
        assert isinstance(capability, BundleIdCapability)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
        assert capability.attributes.capabilityType is capability_type

    def test_disable_capability(self):
        capability_id = ResourceId('F88J43FA9J_ACCESS_WIFI_INFORMATION')
        self.api_client.bundle_id_capabilities.disable(capability_id)

    def test_disable_capability_does_not_exist(self):
        capability_id = ResourceId('F88J43FA9J_ACCESS_WIFI_INFORMATION')
        with pytest.raises(AppStoreConnectApiError) as exception_info:
            self.api_client.bundle_id_capabilities.disable(capability_id)
        error = exception_info.value.error_response.errors[0]
        assert error.code == 'NOT_FOUND'
        assert error.status == '404'

    def test_modify_capability_configuration(self):
        capability = self.api_client.bundle_id_capabilities.modify_configuration(
            ResourceId('F88J43FA9J_GAME_CENTER_IOS'),
            CapabilityType.GAME_CENTER,
            None
        )
        assert isinstance(capability, BundleIdCapability)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
