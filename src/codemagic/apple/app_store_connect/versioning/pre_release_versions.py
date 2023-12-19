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
from codemagic.apple.resources import ResourceVersion

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

    def read(self, pre_release_version: Union[LinkedResourceData, ResourceId]) -> PreReleaseVersion:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_prerelease_version_information
        """
        pre_release_version_id = self._get_resource_id(pre_release_version)
        response = self.client.session.get(f"{self.client.API_URL}/preReleaseVersions/{pre_release_version_id}").json()
        return PreReleaseVersion(response["data"])

    def list(self, resource_filter: Filter = Filter()) -> List[PreReleaseVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_prerelease_versions
        """
        results = self.client.paginate_with_included(
            f"{self.client.API_URL}/preReleaseVersions",
            params=resource_filter.as_query_params(),
        )
        return [PreReleaseVersion(prerelease_version) for prerelease_version in results.data]

    def list_version_numbers(self, resource_filter: Filter = Filter()) -> List[ResourceVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_prerelease_versions
        """
        results = self.client.paginate(
            f"{self.client.API_URL}/preReleaseVersions",
            params={
                "fields[preReleaseVersions]": "version",
                **resource_filter.as_query_params(),
            },
            page_size=200,
        )
        return [ResourceVersion(ResourceId(v["id"]), v["attributes"]["version"]) for v in results]

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

    def list_build_version_numbers(
        self,
        pre_release_version: Union[LinkedResourceData, ResourceId],
        expired: Optional[bool] = None,
    ) -> List[ResourceVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_builds_of_a_prerelease_version
        """
        pre_release_version_id = self._get_resource_id(pre_release_version)
        results = self.client.paginate(
            f"{self.client.API_URL}/preReleaseVersions/{pre_release_version_id}/builds",
            params={"fields[builds]": "version" if expired is None else "version,expired"},
            page_size=200,
        )
        return [
            ResourceVersion(ResourceId(b["id"]), b["attributes"]["version"])
            for b in results
            if expired is None or b["attributes"]["expired"] is expired
        ]
