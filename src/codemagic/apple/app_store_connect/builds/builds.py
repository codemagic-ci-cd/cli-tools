from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import BetaReviewState
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildBetaDetail
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType

IncludedResource = TypeVar("IncludedResource", bound=Resource)


class Builds(ResourceManager[Build]):
    """
    Builds
    https://developer.apple.com/documentation/appstoreconnectapi/builds
    """

    @property
    def resource_type(self) -> Type[Build]:
        return Build

    @dataclass
    class Filter(ResourceManager.Filter):
        app: Optional[ResourceId] = None
        expired: Optional[bool] = None
        id: Optional[ResourceId] = None
        processing_state: Optional[BuildProcessingState] = None
        beta_app_review_submission_beta_review_state: Optional[Union[BetaReviewState, Sequence[BetaReviewState]]] = None
        version: Optional[Union[str, int]] = None
        pre_release_version_version: Optional[str] = None
        pre_release_version_platform: Optional[Platform] = None

        @classmethod
        def _get_field_name(cls, field_name) -> str:
            if field_name == "pre_release_version_version":
                field_name = "pre_release_version.version"
            elif field_name == "pre_release_version_platform":
                field_name = "pre_release_version.platform"
            elif field_name == "beta_app_review_submission_beta_review_state":
                field_name = "beta_app_review_submission.beta_review_state"
            return super()._get_field_name(field_name)

    class Ordering(ResourceManager.Ordering):
        PRE_RELEASE_VERSION = "preReleaseVersion"
        UPLOADED_DATE = "uploadedDate"
        VERSION = "version"
        BETA_REVIEW_STATE = "betaReviewState"

    def read(self, build: Union[LinkedResourceData, ResourceId]) -> Build:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_build_information
        """
        build_id = self._get_resource_id(build)
        response = self.client.session.get(f"{self.client.API_URL}/builds/{build_id}").json()
        return Build(response["data"])

    def list(
        self,
        resource_filter: Filter = Filter(),
        ordering=Ordering.UPLOADED_DATE,
        reverse=False,
    ) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_builds
        """

        params = {"sort": ordering.as_param(reverse), **resource_filter.as_query_params()}
        builds = self.client.paginate(f"{self.client.API_URL}/builds", params=params)
        return [Build(build) for build in builds]

    def read_app(self, build: Union[Build, ResourceId]) -> App:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_information_of_a_build
        """
        url = None
        if isinstance(build, Build) and build.relationships is not None:
            url = build.relationships.app.links.related
        if url is None:
            url = f"{self.client.API_URL}/builds/{build}/app"
        response = self.client.session.get(url).json()
        return App(response["data"])

    def read_app_store_version(self, build: Union[Build, ResourceId]) -> Optional[AppStoreVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_store_version_information_of_a_build
        """
        url = None
        if isinstance(build, Build) and build.relationships is not None:
            url = build.relationships.appStoreVersion.links.related
        if url is None:
            url = f"{self.client.API_URL}/builds/{build}/appStoreVersion"
        response = self.client.session.get(url).json()
        if response["data"] is None:
            return None
        return AppStoreVersion(response["data"])

    def read_pre_release_version(self, build: Union[Build, ResourceId]) -> Optional[PreReleaseVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_prerelease_version_of_a_build
        """
        url = None
        if isinstance(build, Build) and build.relationships is not None:
            url = build.relationships.preReleaseVersion.links.related
        if url is None:
            url = f"{self.client.API_URL}/builds/{build}/preReleaseVersion"
        response = self.client.session.get(url).json()
        if response["data"] is None:
            return None
        return PreReleaseVersion(response["data"])

    def read_beta_detail(self, build: Union[Build, ResourceId]) -> BuildBetaDetail:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_build_beta_details_information_of_a_build
        """
        url = None
        if isinstance(build, Build) and build.relationships is not None:
            url = build.relationships.buildBetaDetail.links.related
        if url is None:
            url = f"{self.client.API_URL}/builds/{build}/buildBetaDetail"
        response = self.client.session.get(url).json()
        return BuildBetaDetail(response["data"])

    def read_with_include(
        self,
        build: Union[LinkedResourceData, ResourceId],
        include_type: Type[IncludedResource],
    ) -> Tuple[Build, IncludedResource]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_build_information
        """
        included_field = self._get_include_field_name(include_type)

        build_id = self._get_resource_id(build)
        response = self.client.session.get(
            f"{self.client.API_URL}/builds/{build_id}",
            params={"include": included_field},
        ).json()

        return Build(response["data"]), include_type(response["included"][0])

    def modify(
        self,
        build: Union[LinkedResourceData, ResourceId],
        expired: Optional[bool] = None,
    ) -> Build:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_build
        """
        build_id = self._get_resource_id(build)

        attributes = {}
        if expired is not None:
            attributes["expired"] = expired

        payload = self._get_update_payload(
            build_id,
            ResourceType.BUILDS,
            attributes=attributes,
        )
        response = self.client.session.patch(
            f"{self.client.API_URL}/builds/{build_id}",
            json=payload,
        ).json()
        return Build(response["data"])

    @classmethod
    def _get_include_field_name(cls, include_type: Type[IncludedResource]) -> str:
        if include_type is App:
            return "app"
        raise ValueError(f"Unknown include type {include_type}")
