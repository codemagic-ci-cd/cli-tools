import os

import pytest

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class AppsTest(ResourceManagerTestsBase):
    def test_list(self):
        apps = self.api_client.apps.list()
        assert len(apps) > 0
        for app in apps:
            assert isinstance(app, App)
            assert app.type is ResourceType.APPS

    def test_read(self):
        app_id = ResourceId('1481211155')
        app = self.api_client.apps.read(app_id)
        print(app.json())
        assert isinstance(app, App)
        assert app.id == app_id
        assert app.type is ResourceType.APPS

    def test_read_not_found(self):
        with pytest.raises(AppStoreConnectApiError) as exception_info:
            self.api_client.apps.read(ResourceId('invalid-id'))
        response = exception_info.value.response
        assert response.status_code == 404


@pytest.mark.parametrize('python_field_name, apple_filter_name', [
    ('bundle_id', 'bundleId'),
    ('app_store_versions_platform', 'appStoreVersions.platform'),
    ('app_store_versions_app_store_state', 'appStoreVersions.appStoreState'),
    ('sku', 'sku'),
])
def test_apps_filter(app_store_connect_api_client, python_field_name, apple_filter_name):
    get_apple_filter_name = app_store_connect_api_client.apps.Filter._get_field_name
    assert get_apple_filter_name(python_field_name) == apple_filter_name
