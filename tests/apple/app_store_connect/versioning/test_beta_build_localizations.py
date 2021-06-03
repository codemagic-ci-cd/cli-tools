import os
import uuid

import pytest

from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BetaBuildLocalizationsTest(ResourceManagerTestsBase):
    def test_list(self):
        resource_filter = self.api_client.beta_build_localizations.Filter(
            build=ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'),
        )
        beta_build_localizations = self.api_client.beta_build_localizations.list(resource_filter)
        assert len(list(beta_build_localizations)) > 0
        for localization in beta_build_localizations:
            assert type(localization) is BetaBuildLocalization
            assert localization.type is ResourceType.BETA_BUILD_LOCALIZATIONS

    def test_delete(self):
        self.api_client.beta_build_localizations.delete(ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'), 'en-GB')

    def test_create(self):
        locale = 'en-GB'
        whats_new = "What's new notes"

        beta_build_localization = self.api_client.beta_build_localizations.create(
            ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'),
            locale=locale,
            whats_new=whats_new,
        )

        assert type(beta_build_localization) is BetaBuildLocalization
        assert beta_build_localization.type is ResourceType.BETA_BUILD_LOCALIZATIONS
        assert beta_build_localization.attributes.dict() == {
            'locale': locale,
            'whatsNew': whats_new,
        }

    def test_modify(self):
        updated_whats_new = f"What's new notes updated {uuid.uuid4()}"
        beta_build_localization = self.api_client.beta_build_localizations.modify(
            ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'),
            locale='en-GB',
            whats_new=updated_whats_new,
        )
        assert type(beta_build_localization) is BetaBuildLocalization
        assert beta_build_localization.type is ResourceType.BETA_BUILD_LOCALIZATIONS
        assert beta_build_localization.attributes.dict() == {
            'locale': 'en-GB',
            'whatsNew': updated_whats_new,
        }
