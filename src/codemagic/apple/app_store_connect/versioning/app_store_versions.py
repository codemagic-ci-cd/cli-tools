from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId


class AppStoreVersions(ResourceManager[AppStoreVersion]):
    """
    App Store Versions
    https://developer.apple.com/documentation/appstoreconnectapi/app_metadata/app_store_versions
    """

    @property
    def resource_type(self) -> Type[AppStoreVersion]:
        return AppStoreVersion

    @dataclass
    class Filter(ResourceManager.Filter):
        version_string: Optional[str] = None

    class Include(ResourceManager.Include):
        BUILD = ('build', Build)

    def list(self,
             application_id: ResourceId,
             resource_filter: Filter = Filter(),
             include: Include = Include.BUILD) -> Tuple[List[AppStoreVersion], List[Resource]]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_versions_for_an_app
        """

        params = {
            'include': include.include_name,
            **resource_filter.as_query_params(),
        }
        results = self.client.paginate_with_included(
            f'{self.client.API_URL}/apps/{application_id}/appStoreVersions', params=params)
        return (
            [AppStoreVersion(app_store_version) for app_store_version in results.data],
            [include.resource_type(included) for included in results.included]
        )
