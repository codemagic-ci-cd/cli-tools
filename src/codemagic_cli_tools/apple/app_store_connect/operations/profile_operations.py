from typing import Optional, List, Union

from apple.resources import Profile
from apple.resources import ProfileState
from apple.resources import ProfileType
from apple.resources import ResourceId
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

    def create(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_profile
        """

    def delete(self):
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

    def read(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_profile_information
        """

    def read_bundle_id(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_bundle_id_in_a_profile
        """

    def get_bundle_id_resource_id(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_the_bundle_resource_id_in_a_profile
        """

    def list_certificates(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_certificates_in_a_profile
        """

    def list_certificate_ids(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_certificate_ids_in_a_profile
        """

    def list_devices(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_devices_in_a_profile
        """

    def list_device_ids(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_device_resource_ids_in_a_profile
        """
