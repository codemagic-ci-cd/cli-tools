import os

import pytest
from codemagic.apple.resources import AppStoreVersionPhasedRelease
from codemagic.apple.resources import PhasedReleaseState
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType

from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(
    not os.environ.get("RUN_LIVE_API_TESTS"),
    reason="Live App Store Connect API access",
)
class AppStoreVersionPhasedReleasesTest(ResourceManagerTestsBase):
    def test_create(self):
        app_store_version_id = ResourceId("409ebefb-ebd1-4f1a-903d-6ba16e013ebf")
        app_store_version_phased_release = self.api_client.app_store_version_phased_releases.create(
            app_store_version_id,
            phased_release_state=PhasedReleaseState.ACTIVE,
        )
        assert isinstance(app_store_version_phased_release, AppStoreVersionPhasedRelease)
        assert app_store_version_phased_release.type is ResourceType.APP_STORE_VERSION_PHASED_RELEASES

    def test_modify(self):
        app_store_version_phased_release_id = ResourceId("409ebefb-ebd1-4f1a-903d-6ba16e013ebf")
        app_store_version_phased_release = self.api_client.app_store_version_phased_releases.modify(
            app_store_version_phased_release_id,
            phased_release_state=PhasedReleaseState.ACTIVE,
        )
        attributes: AppStoreVersionPhasedRelease.Attributes = app_store_version_phased_release.attributes
        print(app_store_version_phased_release)
        assert attributes.phasedReleaseState is PhasedReleaseState.ACTIVE

    def test_delete(self):
        app_store_version_phased_release_id = ResourceId("409ebefb-ebd1-4f1a-903d-6ba16e013ebf")
        self.api_client.app_store_version_phased_releases.delete(app_store_version_phased_release_id)
