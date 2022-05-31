from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import Build
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType

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
        id: Optional[ResourceId] = None
        platform: Optional[Platform] = None
        version_string: Optional[str] = None
        app_store_state: Optional[Union[AppStoreState, Sequence[AppStoreState]]] = None

    @classmethod
    def _get_include_field_name(cls, include_type: Type[IncludedResource]) -> str:
        if include_type is Build:
            return 'build'
        raise ValueError(f'Unknown include type {include_type}')

    def create(
            self,
            platform: Platform,
            version: str,
            app: Union[ResourceId, App],
            build: Optional[Union[ResourceId, Build]] = None,
            copyright: Optional[str] = None,
            earliest_release_date: Optional[datetime] = None,
            release_type: Optional[ReleaseType] = None,
    ) -> AppStoreVersion:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version
        """
        relationships = {
            'app': {
                'data': self._get_attribute_data(app, ResourceType.APPS),
            },
        }
        if build:
            relationships['build'] = {'data': self._get_attribute_data(build, ResourceType.BUILDS)}

        attributes = {
            'platform': platform.value,
            'versionString': version,
        }
        if release_type:
            attributes['releaseType'] = release_type.value
        if copyright:
            attributes['copyright'] = copyright
        if earliest_release_date:
            attributes['earliestReleaseDate'] = Resource.to_iso_8601(earliest_release_date)

        payload = self._get_create_payload(
            ResourceType.APP_STORE_VERSIONS,
            attributes=attributes,
            relationships=relationships,
        )
        response = self.client.session.post(f'{self.client.API_URL}/appStoreVersions', json=payload).json()
        return AppStoreVersion(response['data'], created=True)

    def read(self, app_store_version: Union[LinkedResourceData, ResourceId]) -> AppStoreVersion:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_app_store_version_information
        """
        app_id = self._get_resource_id(app_store_version)
        response = self.client.session.get(f'{self.client.API_URL}/appStoreVersions/{app_id}').json()
        return AppStoreVersion(response['data'])

    def read_build(self, app_store_version: Union[AppStoreVersion, ResourceId]) -> Optional[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_build_information_of_an_app_store_version
        """
        url = None
        if isinstance(app_store_version, AppStoreVersion) and app_store_version.relationships is not None:
            url = app_store_version.relationships.build.links.related
        if url is None:
            url = f'{self.client.API_URL}/appStoreVersions/{app_store_version}/build'
        response = self.client.session.get(url).json()

        if response['data'] is None:
            return None
        return Build(response['data'])

    def read_app_store_version_submission(
            self,
            app_store_version: Union[AppStoreVersion, ResourceId],
    ) -> AppStoreVersionSubmission:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_store_version_submission_information_of_an_app_store_version
        """
        url = None
        if isinstance(app_store_version, AppStoreVersion) and app_store_version.relationships is not None:
            url = app_store_version.relationships.appStoreVersionSubmission.links.related
        if url is None:
            url = f'{self.client.API_URL}/appStoreVersions/{app_store_version}/appStoreVersionSubmission'
        response = self.client.session.get(url).json()
        return AppStoreVersionSubmission(response['data'])

    def list_app_store_version_localizations(
        self,
        app_store_version: Union[LinkedResourceData, ResourceId],
    ) -> List[AppStoreVersionLocalization]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_version_localizations_for_an_app_store_version
        """
        url = None
        if isinstance(app_store_version, AppStoreVersion) and app_store_version.relationships is not None:
            url = app_store_version.relationships.appStoreVersionLocalizations.links.related
        if url is None:
            url = f'{self.client.API_URL}/appStoreVersions/{app_store_version}/appStoreVersionLocalizations'
        return [
            AppStoreVersionLocalization(app_store_version_localization)
            for app_store_version_localization in self.client.paginate(url, page_size=None)
        ]

    def list_with_include(
            self,
            application_id: ResourceId,
            include_type: Type[IncludedResource],
            resource_filter: Filter = Filter()) -> Tuple[List[AppStoreVersion], List[IncludedResource]]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_versions_for_an_app
        """

        # TODO: Move this method under `Apps.list_app_store_versions`

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

    def modify(
            self,
            app_store_version: Union[LinkedResourceData, ResourceId],
            build: Optional[Union[ResourceId, Build]] = None,
            copyright: Optional[str] = None,
            earliest_release_date: Optional[datetime] = None,
            release_type: Optional[ReleaseType] = None,
            version: Optional[str] = None,
    ) -> AppStoreVersion:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version
        """
        attributes = {}
        if copyright:
            attributes['copyright'] = copyright
        if earliest_release_date:
            timestamp = Resource.to_iso_8601(earliest_release_date, with_fractional_seconds=False)
            attributes['earliestReleaseDate'] = timestamp
        if release_type:
            attributes['releaseType'] = release_type.value
        if version:
            attributes['versionString'] = version

        relationships = {}
        if build:
            relationships['build'] = {'data': self._get_attribute_data(build, ResourceType.BUILDS)}

        app_store_version_id = self._get_resource_id(app_store_version)
        payload = self._get_update_payload(
            app_store_version_id,
            ResourceType.APP_STORE_VERSIONS,
            attributes=attributes,
            relationships=relationships,
        )
        response = self.client.session.patch(
            f'{self.client.API_URL}/appStoreVersions/{app_store_version_id}', json=payload).json()
        return AppStoreVersion(response['data'])

    def delete(self, app_store_version: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version
        """
        app_store_version_id = self._get_resource_id(app_store_version)
        self.client.session.delete(f'{self.client.API_URL}/appStoreVersions/{app_store_version_id}')
