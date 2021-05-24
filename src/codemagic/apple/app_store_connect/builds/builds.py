from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId


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
        version: Optional[int] = None
        pre_release_version_version: Optional[str] = None

        @classmethod
        def _get_field_name(cls, field_name) -> str:
            if field_name == 'pre_release_version_version':
                field_name = 'pre_release_version.version'
            return super()._get_field_name(field_name)

    class Ordering(ResourceManager.Ordering):
        PRE_RELEASE_VERSION = 'preReleaseVersion'
        UPLOADED_DATE = 'uploadedDate'
        VERSION = 'version'

    def read(self, build: Union[LinkedResourceData, ResourceId]) -> Build:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_build_information
        """
        build_id = self._get_resource_id(build)
        response = self.client.session.get(f'{self.client.API_URL}/builds/{build_id}').json()
        return Build(response['data'])

    def list(self,
             resource_filter: Filter = Filter(),
             ordering=Ordering.UPLOADED_DATE,
             reverse=False) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_builds
        """

        params = {'sort': ordering.as_param(reverse), **resource_filter.as_query_params()}
        builds = self.client.paginate(f'{self.client.API_URL}/builds', params=params)
        return [Build(build) for build in builds]

    def read_app(self, build: Union[Build, ResourceId]) -> App:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_information_of_a_build
        """
        if isinstance(build, Build):
            url = build.relationships.app.links.related
        else:
            url = f'{self.client.API_URL}/builds/{build}/app'
        response = self.client.session.get(url).json()
        return App(response['data'])

    def read_app_store_version(self, build: Union[Build, ResourceId]) -> Optional[AppStoreVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_store_version_information_of_a_build
        """
        if isinstance(build, Build):
            url = build.relationships.appStoreVersion.links.related
        else:
            url = f'{self.client.API_URL}/builds/{build}/appStoreVersion'
        response = self.client.session.get(url).json()
        if response['data'] is None:
            return None
        return AppStoreVersion(response['data'])

    def read_pre_release_version(self, build: Union[Build, ResourceId]) -> Optional[PreReleaseVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_prerelease_version_of_a_build
        """
        if isinstance(build, Build):
            url = build.relationships.preReleaseVersion.links.related
        else:
            url = f'{self.client.API_URL}/builds/{build}/preReleaseVersion'
        response = self.client.session.get(url).json()
        if response['data'] is None:
            return None
        return PreReleaseVersion(response['data'])
