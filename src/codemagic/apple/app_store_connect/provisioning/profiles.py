from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import Device
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import SigningCertificate


class Profiles(ResourceManager[Profile]):
    """
    Profiles
    https://developer.apple.com/documentation/appstoreconnectapi/profiles
    """

    @property
    def resource_type(self) -> Type[Profile]:
        return Profile

    @dataclass
    class Filter(ResourceManager.Filter):
        id: Optional[Union[str, ResourceId]] = None
        name: Optional[str] = None
        profile_state: Optional[ProfileState] = None
        profile_type: Optional[ProfileType] = None

        def matches(self, profile: Profile) -> bool:
            return (
                self._field_matches(self.id, profile.id)
                and self._field_matches(self.name, profile.attributes.name)
                and self._field_matches(self.profile_state, profile.attributes.profileState)
                and self._field_matches(self.profile_type, profile.attributes.profileType)
            )

    class Ordering(ResourceManager.Ordering):
        ID = "id"
        NAME = "name"
        PROFILE_STATE = "profileState"
        PROFILE_TYPE = "profileType"

    def create(
        self,
        name: str,
        profile_type: ProfileType,
        bundle_id: Union[ResourceId, BundleId],
        certificates: Union[Sequence[ResourceId], Sequence[SigningCertificate]],
        devices: Union[Sequence[ResourceId], Sequence[Device]],
    ) -> Profile:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_profile
        """
        if profile_type.devices_not_allowed() and devices:
            raise ValueError(f"Cannot assign devices to profile with type {profile_type}")
        elif profile_type.devices_required() and not devices:
            if profile_type.is_tvos_profile:
                device_type = "tvOS"
            elif profile_type.is_macos_profile:
                device_type = "macOS"
            elif profile_type.is_ios_profile:
                device_type = "iOS"
            else:
                raise ValueError(f"Device type for profile type {profile_type} is unknown")

            raise ValueError(
                f"Cannot create profile: the request does not include any {device_type} testing devices "
                f"while they are required for creating a {profile_type} profile. If the profile creation is automatic, "
                "ensure that at least one suitable testing device is registered on the Apple Developer Portal.",
            )

        if devices is None:
            devices = []
        attributes = {
            "name": name,
            "profileType": profile_type.value,
        }
        relationships = {
            "bundleId": {
                "data": self._get_attribute_data(bundle_id, ResourceType.BUNDLE_ID),
            },
            "certificates": {
                "data": [self._get_attribute_data(c, ResourceType.CERTIFICATES) for c in certificates],
            },
            "devices": {
                "data": [self._get_attribute_data(d, ResourceType.DEVICES) for d in devices],
            },
        }
        payload = self._get_create_payload(ResourceType.PROFILES, attributes=attributes, relationships=relationships)
        response = self.client.session.post(f"{self.client.API_URL}/profiles", json=payload).json()
        return Profile(response["data"], created=True)

    def delete(self, profile: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_a_profile
        """
        profile_id = self._get_resource_id(profile)
        self.client.session.delete(f"{self.client.API_URL}/profiles/{profile_id}")

    def list(self, resource_filter: Filter = Filter(), ordering=Ordering.NAME, reverse=False) -> List[Profile]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_and_download_profiles
        """
        params = {"sort": ordering.as_param(reverse), **resource_filter.as_query_params()}
        profiles = self.client.paginate(f"{self.client.API_URL}/profiles", params=params)
        return [Profile(profile) for profile in profiles]

    def read(self, profile: Union[LinkedResourceData, ResourceId]) -> Profile:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_profile_information
        """
        profile_id = self._get_resource_id(profile)
        response = self.client.session.get(f"{self.client.API_URL}/profiles/{profile_id}").json()
        return Profile(response["data"])

    def read_bundle_id(self, profile: Union[Profile, ResourceId]) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_bundle_id_in_a_profile
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.bundleId.links.related
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/bundleId"
        response = self.client.session.get(url).json()
        return BundleId(response["data"])

    def get_bundle_id_resource_id(self, profile: Union[Profile, ResourceId]) -> LinkedResourceData:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/profile/relationships/bundleid
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.bundleId.links.self
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/relationships/bundleId"
        response = self.client.session.get(url).json()
        return LinkedResourceData(response["data"])

    def list_certificates(self, profile: Union[Profile, ResourceId]) -> List[SigningCertificate]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_certificates_in_a_profile
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.certificates.links.self
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/certificates"
        return [SigningCertificate(certificate) for certificate in self.client.paginate(url)]

    def list_certificate_ids(self, profile: Union[Profile, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/profile/relationships/certificates
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.certificates.links.related
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/relationships/certificates"
        return [LinkedResourceData(certificate) for certificate in self.client.paginate(url)]

    def list_devices(self, profile: Union[Profile, ResourceId]) -> List[Device]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_devices_in_a_profile
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.devices.links.self
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/devices"
        return [Device(device) for device in self.client.paginate(url)]

    def list_device_ids(self, profile: Union[Profile, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/profile/relationships/devices
        """
        url = None
        if isinstance(profile, Profile) and profile.relationships is not None:
            url = profile.relationships.devices.links.related
        if url is None:
            url = f"{self.client.API_URL}/profiles/{profile}/relationships/devices"
        return [LinkedResourceData(device) for device in self.client.paginate(url)]
