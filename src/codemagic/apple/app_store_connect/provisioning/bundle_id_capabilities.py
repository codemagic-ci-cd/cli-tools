from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdCapability
from codemagic.apple.resources import CapabilitySetting
from codemagic.apple.resources import CapabilityType
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class BundleIdCapabilities(ResourceManager[BundleIdCapability]):
    """
    Bundle ID Capabilities
    https://developer.apple.com/documentation/appstoreconnectapi/bundle_id_capabilities
    """

    @property
    def resource_type(self) -> Type[BundleIdCapability]:
        return BundleIdCapability

    def enable(self,
               capability_type: CapabilityType,
               bundle_id: Union[ResourceId, BundleId],
               capability_settings: Optional[CapabilitySetting] = None) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/enable_a_capability
        """
        attributes = {'capabilityType': capability_type.value}
        if capability_settings is not None:
            attributes['settings'] = capability_settings.dict()
        relationships = {
            'bundleId': {'data': self._get_attribute_data(bundle_id, ResourceType.BUNDLE_ID)}
        }
        payload = self._get_create_payload(
            ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes, relationships=relationships)
        response = self.client.session.post(f'{self.client.API_URL}/bundleIdCapabilities', json=payload).json()
        return BundleIdCapability(response['data'], created=True)

    def disable(self, bundle_id_capability: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/disable_a_capability
        """
        bundle_id_capability_id = self._get_resource_id(bundle_id_capability)
        self.client.session.delete(f'{self.client.API_URL}/bundleIdCapabilities/{bundle_id_capability_id}')

    def modify_configuration(self,
                             bundle_id_capability: Union[LinkedResourceData, ResourceId],
                             capability_type: CapabilityType,
                             settings: Optional[CapabilitySetting]) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_capability_configuration
        """
        bundle_id_capability_id = self._get_resource_id(bundle_id_capability)
        attributes = {'capabilityType': capability_type.value}
        if settings:
            attributes['settings'] = settings.dict()
        payload = self._get_update_payload(
            bundle_id_capability_id, ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes)
        response = self.client.session.patch(
            f'{self.client.API_URL}/bundleIdCapabilities/{bundle_id_capability_id}', json=payload).json()
        return BundleIdCapability(response['data'])
