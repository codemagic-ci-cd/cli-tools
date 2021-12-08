import os

import pytest

from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import ResourceId
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class AppStoreVersionLocalizationsTest(ResourceManagerTestsBase):
    def test_read(self):
        app_store_localization_id = ResourceId('253cf0c8-8057-49b7-be16-3b1cc78837e5')
        app_store_localization = self.api_client.app_store_version_localizations.read(
            app_store_localization_id,
        )
        assert isinstance(app_store_localization, AppStoreVersionLocalization)
        assert app_store_localization.id == app_store_localization_id
