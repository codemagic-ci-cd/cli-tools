from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId

IncludedResource = TypeVar('IncludedResource', bound=Resource)


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
        platform: Optional[Platform] = None
        version_string: Optional[str] = None

    @classmethod
    def _get_include_field_name(cls, include_type: Type[IncludedResource]) -> str:
        if include_type is Build:
            return 'build'
        raise ValueError(f'Unknown include type {include_type}')

    def list_with_include(
            self,
            application_id: ResourceId,
            include_type: Type[IncludedResource],
            resource_filter: Filter = Filter()) -> Tuple[List[AppStoreVersion], List[IncludedResource]]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_versions_for_an_app
        """

        params = {
            'include': self._get_include_field_name(include_type),
            **resource_filter.as_query_params(),
        }
        results = self.client.paginate_with_included(
            f'{self.client.API_URL}/apps/{application_id}/appStoreVersions', params=params)
        return (
            [AppStoreVersion(app_store_version) for app_store_version in results.data],
            [include_type(included) for included in results.included],
        )
