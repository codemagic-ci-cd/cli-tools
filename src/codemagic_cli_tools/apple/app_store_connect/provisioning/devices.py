from typing import List
from typing import Optional
from typing import Union

from codemagic_cli_tools.apple.app_store_connect.resource_manager import ResourceManager
from codemagic_cli_tools.apple.resources import BundleIdPlatform
from codemagic_cli_tools.apple.resources import Device
from codemagic_cli_tools.apple.resources import DeviceStatus
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType


class DeviceOrdering(ResourceManager.Ordering):
    ID = 'id'
    NAME = 'name'
    PLATFORM = 'platform'
    STATUS = 'status'
    UDID = 'udid'


class Devices(ResourceManager):
    """
    Devices
    https://developer.apple.com/documentation/appstoreconnectapi/devices
    """

    def register(self, name: str, platform: BundleIdPlatform, udid: str) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/register_a_new_device
        """
        attributes = {
            'name': name,
            'platform': platform.value,
            'udid': udid,
        }
        response = self.client.session.post(
            f'{self.client.API_URL}/devices',
            json=self._get_create_payload(ResourceType.DEVICES, attributes=attributes)
        ).json()
        return Device(response['data'])

    def list(self,
             filter_id: Optional[Union[str, ResourceId]] = None,
             filter_name: Optional[str] = None,
             filter_platform: Optional[BundleIdPlatform] = None,
             filter_status: Optional[DeviceStatus] = None,
             filter_udid: Optional[str] = None,
             ordering=DeviceOrdering.NAME,
             reverse=False) -> List[Device]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_devices
        """
        params = {'sort': ordering.as_param(reverse)}
        if filter_id is not None:
            params['filter[id]'] = filter_id
        if filter_name is not None:
            params['filter[name]'] = filter_name
        if filter_platform is not None:
            params['filter[platform]'] = filter_platform.value
        if filter_status is not None:
            params['filter[status]'] = filter_status.value
        if filter_udid is not None:
            params['filter[udid]'] = filter_udid

        devices = self.client.paginate(f'{self.client.API_URL}/devices', params=params)
        return [Device(device) for device in devices]

    def read(self, device: Union[LinkedResourceData, ResourceId]) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_device_information
        """
        device_id = self._get_resource_id(device)
        response = self.client.session.get(f'{self.client.API_URL}/devices/{device_id}').json()
        return Device(response['data'])

    def modify(self,
               device: Union[LinkedResourceData, ResourceId],
               name: Optional[str] = None,
               status: Optional[DeviceStatus] = None) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_registered_device
        """
        device_id = self._get_resource_id(device)
        attributes = {}
        if name is not None:
            attributes['name'] = name
        if status is not None:
            attributes['status'] = status.value
        payload = self._get_update_payload(device_id, ResourceType.DEVICES, attributes=attributes)
        response = self.client.session.patch(f'{self.client.API_URL}/devices/{device_id}', json=payload).json()
        return Device(response['data'])
