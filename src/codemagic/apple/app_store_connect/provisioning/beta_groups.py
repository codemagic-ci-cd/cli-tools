from dataclasses import dataclass
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BetaGroup
from codemagic.apple.resources import Build
from codemagic.apple.resources import LinkedResourceData
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
        id: Optional[Union[str, ResourceId]] = None
        name: Optional[str] = None
        app: Optional[str] = None

    def list(self, resource_filter: Filter = Filter()):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_beta_groups
        """
        # add a non-breakable space in the name of the automatically created internal group
        if resource_filter.name == 'App Store Connect Users':
            resource_filter.name = 'App\xa0Store Connect Users'

        params = {**resource_filter.as_query_params()}
        beta_groups = self.client.paginate(f'{self.client.API_URL}/betaGroups', params)

        return [BetaGroup(beta_group) for beta_group in beta_groups]

    def modify_add_build(self, beta_group: Union[ResourceId, BetaGroup], build: Union[ResourceId, Build]):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/add_builds_to_a_beta_group
        """
        beta_group_resource_id = self._get_resource_id(beta_group)
        build_resource_id = self._get_resource_id(build)

        payload = {
            'data': [
                self._get_attribute_data(build_resource_id, resource_type=ResourceType.BUILDS)
            ]
        }
        self.client.session.post(
            f'{self.client.API_URL}/betaGroups/{beta_group_resource_id}/relationships/builds', json=payload)

    def modify_remove_build(self, beta_group: Union[ResourceId, BetaGroup], build: Union[ResourceId, Build]):
        beta_group_resource_id = self._get_resource_id(beta_group)
        build_resource_id = self._get_resource_id(build)

        payload = {
            'data': [
                self._get_attribute_data(build_resource_id, resource_type=ResourceType.BUILDS)
            ]
        }
        self.client.session.delete(
            f'{self.client.API_URL}/betaGroups/{beta_group_resource_id}/relationships/builds', json=payload)
