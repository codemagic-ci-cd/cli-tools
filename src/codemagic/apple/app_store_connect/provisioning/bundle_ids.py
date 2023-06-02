from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdCapability
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType

if TYPE_CHECKING:
    from .profiles import Profiles


class BundleIds(ResourceManager[BundleId]):
    """
    Bundle IDs
    https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids
    """

    @property
    def resource_type(self) -> Type[BundleId]:
        return BundleId

    @dataclass
    class Filter(ResourceManager.Filter):
        id: Optional[str] = None
        identifier: Optional[str] = None
        name: Optional[str] = None
        platform: Optional[BundleIdPlatform] = None
        seed_id: Optional[str] = None

        def matches(self, bundle_id: BundleId) -> bool:
            # Double check that platform matches since this filter does not work on Apple's
            # side as of 02.03.2021 and API 1.2. All other filters are applied as expected.
            # In case either platform 'IOS' or 'MAC_OS' is specified, then we need to also
            # accept bundle ids with platform 'UNIVERSAL' since it covers both.
            if not self.platform:
                return True
            return bundle_id.attributes.platform in (self.platform, BundleIdPlatform.UNIVERSAL)

    class Ordering(ResourceManager.Ordering):
        ID = 'id'
        NAME = 'name'
        PLATFORM = 'platform'
        SEED_ID = 'seedId'

    def create(self,
               identifier: str,
               name: str,
               platform: BundleIdPlatform,
               seed_id: Optional[str] = None) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/register_a_new_bundle_id
        """
        attributes = {
            'name': name,
            'identifier': identifier,
            'platform': platform.value,
        }
        if seed_id:
            attributes['seedId'] = seed_id
        response = self.client.session.post(
            f'{self.client.API_URL}/bundleIds',
            json=self._get_create_payload(ResourceType.BUNDLE_ID, attributes=attributes),
        ).json()
        return BundleId(response['data'], created=True)

    def modify(self, bundle_id: Union[LinkedResourceData, ResourceId], name: str) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_bundle_id
        """
        bundle_id_resource_id = self._get_resource_id(bundle_id)
        payload = self._get_update_payload(bundle_id_resource_id, ResourceType.BUNDLE_ID, attributes={'name': name})
        response = self.client.session.patch(
            f'{self.client.API_URL}/bundleIds/{bundle_id_resource_id}', json=payload).json()
        return BundleId(response['data'])

    def delete(self, bundle_id: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_a_bundle_id
        """
        bundle_id_resource_id = self._get_resource_id(bundle_id)
        self.client.session.delete(f'{self.client.API_URL}/bundleIds/{bundle_id_resource_id}')

    def list(self,
             resource_filter: Filter = Filter(),
             ordering=Ordering.NAME,
             reverse=False) -> List[BundleId]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_bundle_ids
        """
        params = {'sort': ordering.as_param(reverse), **resource_filter.as_query_params()}
        url = f'{self.client.API_URL}/bundleIds'
        bundle_ids = (BundleId(bundle_id) for bundle_id in self.client.paginate(url, params=params))
        return [bundle_id for bundle_id in bundle_ids if resource_filter.matches(bundle_id)]

    def read(self, bundle_id: Union[LinkedResourceData, ResourceId]) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_bundle_id_information
        """
        bundle_id_resource_id = self._get_resource_id(bundle_id)
        response = self.client.session.get(f'{self.client.API_URL}/bundleIds/{bundle_id_resource_id}').json()
        return BundleId(response['data'])

    def list_profile_ids(self, bundle_id: Union[BundleId, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_profile_ids_for_a_bundle_id
        """
        url = None
        if isinstance(bundle_id, BundleId) and bundle_id.relationships is not None:
            url = bundle_id.relationships.profiles.links.self
        if url is None:
            url = f'{self.client.API_URL}/bundleIds/{bundle_id}/relationships/profiles'
        return [LinkedResourceData(bundle_id_profile) for bundle_id_profile in self.client.paginate(url)]

    def list_profiles(self,
                      bundle_id: Union[BundleId, ResourceId],
                      resource_filter: Optional[Profiles.Filter] = None) -> List[Profile]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_profiles_for_a_bundle_id
        """
        url = None
        if isinstance(bundle_id, BundleId) and bundle_id.relationships is not None:
            url = bundle_id.relationships.profiles.links.related
        if url is None:
            url = f'{self.client.API_URL}/bundleIds/{bundle_id}/profiles'
        profiles = [Profile(profile) for profile in self.client.paginate(url)]
        if resource_filter:
            return [profile for profile in profiles if resource_filter.matches(profile)]
        return profiles

    def list_capabilility_ids(self, bundle_id: Union[BundleId, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_capabilility_ids_for_a_bundle_id
        """
        url = None
        if isinstance(bundle_id, BundleId) and bundle_id.relationships is not None:
            url = bundle_id.relationships.bundleIdCapabilities.links.self
        if url is None:
            url = f'{self.client.API_URL}/bundleIds/{bundle_id}/relationships/bundleIdCapabilities'
        return [LinkedResourceData(capabilility) for capabilility in self.client.paginate(url, page_size=None)]

    def list_capabilities(self, bundle_id: Union[BundleId, ResourceId]) -> List[BundleIdCapability]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_capabilities_for_a_bundle_id
        """
        url = None
        if isinstance(bundle_id, BundleId) and bundle_id.relationships is not None:
            url = bundle_id.relationships.bundleIdCapabilities.links.related
        if url is None:
            url = f'{self.client.API_URL}/bundleIds/{bundle_id}/bundleIdCapabilities'
        return [BundleIdCapability(capabilility) for capabilility in self.client.paginate(url, page_size=None)]
