from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Sequence
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

    def list_data(
        self,
        resource_filter: Filter = Filter(),
        limit: Optional[int] = None,
        fields: Sequence[str] = tuple(),
        page_size: Optional[int] = 100,
    ) -> List[dict]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_prerelease_versions
        """
        params = resource_filter.as_query_params()
        if fields:
            params["fields[preReleaseVersions]"] = ",".join(fields)
        url = f"{self.client.API_URL}/preReleaseVersions"
        return self.client.paginate(url, params=params, limit=limit, page_size=page_size)

    def list(self, resource_filter: Filter = Filter()) -> List[PreReleaseVersion]:
        pre_release_versions_data = self.list_data(resource_filter=resource_filter)
        return [PreReleaseVersion(prerelease_version) for prerelease_version in pre_release_versions_data]

    def list_builds_data(
        self,
        pre_release_version: Union[LinkedResourceData, ResourceId],
        limit: Optional[int] = None,
        fields: Sequence[str] = tuple(),
        page_size: Optional[int] = 100,
    ) -> List[dict]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_builds_of_a_prerelease_version
        """
        pre_release_version_id = self._get_resource_id(pre_release_version)
        url = f"{self.client.API_URL}/preReleaseVersions/{pre_release_version_id}/builds"
        params = {"fields[builds]": ",".join(fields)} if fields else {}
        return self.client.paginate(url, params=params, limit=limit, page_size=page_size)

    def list_builds(self, pre_release_version: Union[LinkedResourceData, ResourceId]) -> List[Build]:
        builds_data = self.list_builds_data(pre_release_version, page_size=None)
        return [Build(build) for build in builds_data]
