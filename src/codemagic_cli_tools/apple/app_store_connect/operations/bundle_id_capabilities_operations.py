from typing import Optional
from typing import Union

from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import BundleIdCapability
from codemagic_cli_tools.apple.resources import CapabilitySetting
from codemagic_cli_tools.apple.resources import CapabilityType
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType
from .base_operations import BaseOperations


class BundleIdCapabilitiesOperations(BaseOperations):
    """
    Bundle ID Capabilities operations
    https://developer.apple.com/documentation/appstoreconnectapi/bundle_id_capabilities
    """

    def enable(self,
               capability_type: CapabilityType,
               bundle_id_resource: Union[ResourceId, BundleId],
               capability_settings: Optional[CapabilitySetting] = None) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/enable_a_capability
        """
        if isinstance(bundle_id_resource, BundleId):
            bundle_id = bundle_id_resource.id
        else:
            bundle_id = bundle_id_resource

        attributes = {'capabilityType': capability_type.value}
        if capability_settings is not None:
            attributes['settings'] = capability_settings.dict()
        relationships = {
            'bundleId': {
                'data': {'id': bundle_id, 'type': ResourceType.BUNDLE_ID.value}
            }
        }
        payload = self.client.get_create_payload(
            ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes, relationships=relationships)
        response = self.client.session.post(f'{self.client.API_URL}/bundleIdCapabilities', json=payload).json()
        return BundleIdCapability(response['data'])

    def disable(self, resource: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/disable_a_capability
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        self.client.session.delete(f'{self.client.API_URL}/bundleIdCapabilities/{resource_id}')

    def modify_configuration(self,
                             resource: Union[LinkedResourceData, ResourceId],
                             capability_type: CapabilityType,
                             settings: Optional[CapabilitySetting]) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_capability_configuration
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        attributes = {'capabilityType': capability_type.value}
        if settings:
            attributes['settings'] = settings.dict()
        payload = self.client.get_update_payload(
            resource_id, ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes)
        response = self.client.session.patch(
            f'{self.client.API_URL}/bundleIdCapabilities/{resource_id}', json=payload).json()
        return BundleIdCapability(response['data'])
