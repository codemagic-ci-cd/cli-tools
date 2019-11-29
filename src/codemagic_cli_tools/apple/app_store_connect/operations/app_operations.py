from typing import List

from codemagic_cli_tools.apple.resources import App
from .base_operations import BaseOperations
from .base_operations import BaseOrdering


class AppOrdering(BaseOrdering):
    BUNDLE_ID = 'bundleId'
    NAME = 'name'
    SKU = 'sku'


class AppOperations(BaseOperations):
    """
    App operations
    https://developer.apple.com/documentation/appstoreconnectapi/testflight/apps
    """

    def list(self, ordering=AppOrdering.NAME, reverse=False) -> List[App]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_apps
        """
        params = {'sort': ordering.as_param(reverse)}
        apps = self.client.paginate(f'{self.client.API_URL}/apps', params=params)
        return [App(app) for app in apps]
