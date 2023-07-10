from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import Device
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class Devices(ResourceManager[Device]):
    """
    Devices
    https://developer.apple.com/documentation/appstoreconnectapi/devices
    """

    @property
    def resource_type(self) -> Type[Device]:
        return Device

    @dataclass
    class Filter(ResourceManager.Filter):
        id: Optional[Union[str, ResourceId]] = None
        name: Optional[str] = None
        platform: Optional[BundleIdPlatform] = None
        status: Optional[DeviceStatus] = None
        udid: Optional[str] = None

    class Ordering(ResourceManager.Ordering):
        ID = "id"
        NAME = "name"
        PLATFORM = "platform"
        STATUS = "status"
        UDID = "udid"

    def create(self, name: str, platform: BundleIdPlatform, udid: str) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/register_a_new_device
        """
        attributes = {
            "name": name,
            "platform": platform.value,
            "udid": udid,
        }
        response = self.client.session.post(
            f"{self.client.API_URL}/devices",
            json=self._get_create_payload(ResourceType.DEVICES, attributes=attributes),
        ).json()
        return Device(response["data"], created=True)

    def list(self, resource_filter: Filter = Filter(), ordering=Ordering.NAME, reverse=False) -> List[Device]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_devices
        """
        params = {"sort": ordering.as_param(reverse), **resource_filter.as_query_params()}
        devices = self.client.paginate(f"{self.client.API_URL}/devices", params=params)
        return [Device(device) for device in devices]

    def read(self, device: Union[LinkedResourceData, ResourceId]) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_device_information
        """
        device_id = self._get_resource_id(device)
        response = self.client.session.get(f"{self.client.API_URL}/devices/{device_id}").json()
        return Device(response["data"])

    def modify(
        self,
        device: Union[LinkedResourceData, ResourceId],
        name: Optional[str] = None,
        status: Optional[DeviceStatus] = None,
    ) -> Device:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_registered_device
        """
        device_id = self._get_resource_id(device)
        attributes = {}
        if name is not None:
            attributes["name"] = name
        if status is not None:
            attributes["status"] = status.value
        payload = self._get_update_payload(device_id, ResourceType.DEVICES, attributes=attributes)
        response = self.client.session.patch(f"{self.client.API_URL}/devices/{device_id}", json=payload).json()
        return Device(response["data"])
