from typing import Optional, List, Union

from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import Certificate
from codemagic_cli_tools.apple.resources import Profile
from codemagic_cli_tools.apple.resources import Device
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ProfileState
from codemagic_cli_tools.apple.resources import ProfileType
from codemagic_cli_tools.apple.resources import ResourceId
from .base_operations import BaseOperations
from .base_operations import BaseOrdering


class ProfileOrdering(BaseOrdering):
    ID = 'id'
    NAME = 'name'
    PROFILE_STATE = 'profileState'
    PROFILE_TYPE = 'profileType'


class ProfileOperations(BaseOperations):
    """
    Profiles operations
    https://developer.apple.com/documentation/appstoreconnectapi/profiles
    """

    def create(self) -> Profile:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_profile
        """

    def delete(self) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_a_profile
        """

    def list(self,
             filter_id: Optional[Union[str, ResourceId]] = None,
             filter_name: Optional[str] = None,
             filter_profile_state: Optional[ProfileState] = None,
             filter_profile_type: Optional[ProfileType] = None,
             ordering=ProfileOrdering.NAME,
             reverse=False) -> List[Profile]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_and_download_profiles
        """
        params = {'sort': ordering.as_param(reverse)}
        if filter_id is not None:
            params['filter[id]'] = filter_id
        if filter_profile_state is not None:
            params['filter[profileState]'] = filter_profile_state.value
        if filter_profile_type is not None:
            params['filter[profileType]'] = filter_profile_type.value
        if filter_name is not None:
            params['filter[name]'] = filter_name

        profiles = self.client.paginate(f'{self.client.API_URL}/profiles', params=params)
        return [Profile(profile) for profile in profiles]

    def read(self, resource: Union[LinkedResourceData, ResourceId]) -> Profile:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_profile_information
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        response = self.client.session.get(f'{self.client.API_URL}/profiles/{resource_id}').json()
        return Profile(response['data'])

    def read_bundle_id(self, resource: Union[Profile, ResourceId]) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_bundle_id_in_a_profile
        """
        if isinstance(resource, Profile):
            url = resource.relationships.bundleId.links.related
        else:
            url = f'{self.client.API_URL}/profiles/{resource}/bundleId'
        response = self.client.session.get(url).json()
        return BundleId(response['data'])

    def get_bundle_id_resource_id(self, resource: Union[Profile, ResourceId]) -> LinkedResourceData:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_the_bundle_resource_id_in_a_profile
        """
        if isinstance(resource, Profile):
            url = resource.relationships.bundleId.links.self
        else:
            url = f'{self.client.API_URL}/profiles/{resource}/relationships/bundleId'
        response = self.client.session.get(url).json()
        return LinkedResourceData(response['data'])

    def list_certificates(self, resource: Union[Profile, ResourceId]) -> List[Certificate]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_certificates_in_a_profile
        """
        if isinstance(resource, Profile):
            url = resource.relationships.profiles.links.related
        else:
            url = f'{self.client.API_URL}/profiles/{resource}/certificates'
        return [Certificate(certificate) for certificate in self.client.paginate(url)]

    def list_certificate_ids(self, resource: Union[Profile, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_certificate_ids_in_a_profile
        """
        if isinstance(resource, Profile):
            url = resource.relationships.profiles.links.self
        else:
            url = f'{self.client.API_URL}/profiles/{resource}/relationships/certificates'
        return [LinkedResourceData(certificate) for certificate in self.client.paginate(url)]

    def list_devices(self, resource: Union[Profile, ResourceId]) -> List[Device]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_devices_in_a_profile
        """

    def list_device_ids(self, resource: Union[Profile, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_device_resource_ids_in_a_profile
        """
