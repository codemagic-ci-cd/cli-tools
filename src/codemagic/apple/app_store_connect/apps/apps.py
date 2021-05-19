from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import Platform
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

    def read(self, app_id: ResourceId):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_app_information
        """
        ...  # TODO
