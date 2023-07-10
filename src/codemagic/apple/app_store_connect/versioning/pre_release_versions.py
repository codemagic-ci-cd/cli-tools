from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Build
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId

IncludedResource = TypeVar("IncludedResource", bound=Resource)


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
            return "builds"
        raise ValueError(f"Unknown include type {include_type}")

    def list(self, resource_filter: Filter = Filter()) -> List[PreReleaseVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_prerelease_versions
        """
        results = self.client.paginate_with_included(
            f"{self.client.API_URL}/preReleaseVersions",
            params=resource_filter.as_query_params(),
        )
        return [PreReleaseVersion(prerelease_version) for prerelease_version in results.data]

    def list_builds(self, pre_release_version: Union[LinkedResourceData, ResourceId]) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_builds_of_a_prerelease_version
        """

        url = None
        if isinstance(pre_release_version, PreReleaseVersion) and pre_release_version.relationships is not None:
            url = pre_release_version.relationships.builds.links.related
        if url is None:
            url = f"{self.client.API_URL}/preReleaseVersions/{pre_release_version}/builds"

        return [Build(build) for build in self.client.paginate(url, page_size=None)]
