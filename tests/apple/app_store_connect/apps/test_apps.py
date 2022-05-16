import os

import pytest

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect.apps import Apps
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
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

    def test_read_beta_app_localizations(self):
        banaan_app_id = ResourceId('1481211155')  # Banaan iOS
        capybara_app_id = ResourceId('1496105355')  # CapybaraApp
        for app_id in (banaan_app_id, capybara_app_id):
            beta_app_localizations = self.api_client.apps.list_beta_app_localizations(app_id)
            for beta_app_localization in beta_app_localizations:
                assert beta_app_localization.type is ResourceType.BETA_APP_LOCALIZATIONS
                assert beta_app_localization.relationships.app

    def test_read_beta_app_review_detail(self):
        banaan_app_id = ResourceId('1481211155')  # Banaan iOS
        capybara_app_id = ResourceId('1496105355')  # CapybaraApp
        for app_id in (banaan_app_id, capybara_app_id):
            beta_app_review_detail = self.api_client.apps.read_beta_app_review_detail(app_id)
            assert beta_app_review_detail.type is ResourceType.BETA_APP_REVIEW_DETAILS
            assert beta_app_review_detail.relationships.app

    def test_read_not_found(self):
        with pytest.raises(AppStoreConnectApiError) as exception_info:
            self.api_client.apps.read(ResourceId('invalid-id'))
        response = exception_info.value.response
        assert response.status_code == 404

    def test_list_app_store_versions(self):
        banaan_app_id = ResourceId('1481211155')  # Banaan iOS
        versions_filter = self.api_client.app_store_versions.Filter(
            app_store_state=[AppStoreState.IN_REVIEW, AppStoreState.REJECTED],
        )
        app_store_versions = self.api_client.apps.list_app_store_versions(
            banaan_app_id,
            resource_filter=versions_filter,
        )
        assert len(app_store_versions) == 1
        app_store_version = app_store_versions[0]
        assert app_store_version.attributes.appStoreState is AppStoreState.REJECTED


@pytest.mark.parametrize('python_field_name, apple_filter_name', [
    ('bundle_id', 'bundleId'),
    ('app_store_versions_platform', 'appStoreVersions.platform'),
    ('app_store_versions_app_store_state', 'appStoreVersions.appStoreState'),
    ('sku', 'sku'),
])
def test_apps_filter(python_field_name, apple_filter_name):
    get_apple_filter_name = Apps.Filter._get_field_name
    assert get_apple_filter_name(python_field_name) == apple_filter_name
