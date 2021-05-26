from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.app_store_connect.versioning import AppStoreVersions
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId


class Apps(ResourceManager[App]):
    """
    Apps
    https://developer.apple.com/documentation/appstoreconnectapi/apps
    """

    @property
    def resource_type(self) -> Type[App]:
        return App

    @dataclass
    class Filter(ResourceManager.Filter):
        bundle_id: Optional[str] = None
        id: Optional[ResourceId] = None
        name: Optional[str] = None
        sku: Optional[str] = None
        app_store_versions: Optional[str] = None
        app_store_versions_platform: Optional[Platform] = None
        app_store_versions_app_store_state: Optional[AppStoreState] = None

        @classmethod
        def _get_field_name(cls, field_name) -> str:
            if field_name == 'app_store_versions_platform':
                field_name = 'app_store_versions.platform'
            elif field_name == 'app_store_versions_app_store_state':
                field_name = 'app_store_versions.app_store_state'
            return super()._get_field_name(field_name)

    class Ordering(ResourceManager.Ordering):
        BUNDLE_ID = 'bundleId'
        NAME = 'name'
        SKU = 'sku'

    def list(self,
             resource_filter: Filter = Filter(),
             ordering=Ordering.NAME,
             reverse=False) -> List[App]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_apps
        """
        params = {'sort': ordering.as_param(reverse), **resource_filter.as_query_params()}
        apps = self.client.paginate(f'{self.client.API_URL}/apps', params=params)
        return [App(app) for app in apps]

    def read(self, app: Union[LinkedResourceData, ResourceId]) -> App:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_app_information
        """
        app_id = self._get_resource_id(app)
        response = self.client.session.get(f'{self.client.API_URL}/apps/{app_id}').json()
        return App(response['data'])

    def list_builds(self, app: Union[LinkedResourceData, ResourceId]) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_builds_of_an_app
        """
        if isinstance(app, App):
            url = app.relationships.builds.links.related
        else:
            url = f'{self.client.API_URL}/apps/{app}/builds'
        return [Build(build) for build in self.client.paginate(url, page_size=None)]

    def list_pre_release_versions(self, app: Union[LinkedResourceData, ResourceId]) -> List[PreReleaseVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_prerelease_versions_for_an_app
        """
        if isinstance(app, App):
            url = app.relationships.preReleaseVersions.links.related
        else:
            url = f'{self.client.API_URL}/apps/{app}/preReleaseVersions'
        return [PreReleaseVersion(version) for version in self.client.paginate(url, page_size=None)]

    def list_app_store_versions(self,
                                app: Union[LinkedResourceData, ResourceId],
                                resource_filter: Optional[AppStoreVersions.Filter] = None) -> List[AppStoreVersion]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_versions_for_an_app
        """
        if isinstance(app, App):
            url = app.relationships.appStoreVersions.links.related
        else:
            url = f'{self.client.API_URL}/apps/{app}/appStoreVersions'
        params = resource_filter.as_query_params() if resource_filter else None
        app_store_versions = self.client.paginate(url, params=params, page_size=None)
        return [AppStoreVersion(app_store_version) for app_store_version in app_store_versions]
