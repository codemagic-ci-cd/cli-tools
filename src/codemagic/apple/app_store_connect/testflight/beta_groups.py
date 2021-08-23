from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BetaGroup
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class BetaGroups(ResourceManager[BetaGroup]):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/prerelease_versions_and_beta_testers/beta_groups
    """

    @property
    def resource_type(self) -> Type[BetaGroup]:
        return BetaGroup

    @dataclass
    class Filter(ResourceManager.Filter):
        id: Optional[ResourceId] = None
        name: Optional[str] = None
        app: Optional[ResourceId] = None

    def list(self, resource_filter: Filter = Filter()) -> List[BetaGroup]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_beta_groups
        """
        response = self.client.paginate(
            f'{self.client.API_URL}/betaGroups',
            params=resource_filter.as_query_params(),
        )

        return [BetaGroup(item) for item in response]

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
