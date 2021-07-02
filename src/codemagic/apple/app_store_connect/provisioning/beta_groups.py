from dataclasses import dataclass
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.api_error import AppStoreConnectApiError
from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BetaGroup
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class BetaGroups(ResourceManager[BetaGroup]):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betagroup
    """

    @property
    def resource_type(self) -> Type[BetaGroup]:
        return BetaGroup

    @dataclass
    class Filter(ResourceManager.Filter):
        id: Optional[ResourceId] = None
        name: Optional[str] = None
        app: Optional[str] = None

    def list(self, resource_filter: Filter = Filter()):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_beta_groups
        """
        # avoid filtering by name to avoid missing matches that contain non-breakable space symbols
        name = resource_filter.name
        resource_filter.name = None

        params = {**resource_filter.as_query_params()}
        response = self.client.paginate(f'{self.client.API_URL}/betaGroups', params)

        beta_groups = [BetaGroup(item) for item in response]
        return [
            beta_group for beta_group in beta_groups
            if name and self._are_names_equal(name, beta_group.attributes.name)
        ]

    def add_build(self, beta_group: Union[ResourceId, BetaGroup], build: Union[ResourceId, Build]):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/add_builds_to_a_beta_group
        """
        beta_group_resource_id = self._get_resource_id(beta_group)
        build_resource_id = self._get_resource_id(build)

        payload = {
            'data': [
                self._get_attribute_data(build_resource_id, resource_type=ResourceType.BUILDS),
            ],
        }
        self.client.session.post(
            f'{self.client.API_URL}/betaGroups/{beta_group_resource_id}/relationships/builds', json=payload)

    def remove_build(self, beta_group: Union[ResourceId, BetaGroup], build: Union[ResourceId, Build]):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/remove_builds_from_a_beta_group
        """
        beta_group_resource_id = self._get_resource_id(beta_group)
        build_resource_id = self._get_resource_id(build)

        payload = {
            'data': [
                self._get_attribute_data(build_resource_id, resource_type=ResourceType.BUILDS),
            ],
        }
        self.client.session.delete(
            f'{self.client.API_URL}/betaGroups/{beta_group_resource_id}/relationships/builds', json=payload)

    @staticmethod
    def _are_names_equal(name: str, other_name: str):
        """
        Compare names disregarding non-breakable space symbols
        """
        return name.replace('\xa0', ' ') == other_name.replace('\xa0', ' ')
