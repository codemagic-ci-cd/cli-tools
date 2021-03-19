from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId

IncludedResource = TypeVar('IncludedResource', bound=Resource)


class PreReleaseVersions(ResourceManager[PreReleaseVersion]):
    """
    Prerelease Versions
    https://developer.apple.com/documentation/appstoreconnectapi/prerelease_versions_and_beta_testers/prerelease_versions
    """

    @property
    def resource_type(self) -> Type[PreReleaseVersion]:
        return PreReleaseVersion

    @dataclass
    class Filter(ResourceManager.Filter):
        app: Optional[ResourceId] = None
        platform: Optional[Platform] = None
        version: Optional[str] = None

    @classmethod
    def _get_include_field_name(cls, include_type: Type[IncludedResource]) -> str:
        if include_type is Build:
            return 'builds'
        raise ValueError(f'Unknown include type {include_type}')

    def list_with_include(
            self,
            include_type: Type[IncludedResource],
            resource_filter: Filter = Filter()) -> Tuple[List[PreReleaseVersion], List[IncludedResource]]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_prerelease_versions
        """

        params = {
            'include': self._get_include_field_name(include_type),
            **resource_filter.as_query_params(),
        }
        results = self.client.paginate_with_included(f'{self.client.API_URL}/preReleaseVersions', params=params)
        return (
            [PreReleaseVersion(prerelease_version) for prerelease_version in results.data],
            [include_type(included) for included in results.included],
        )
