import os

import pytest

from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class AppStoreVersionsTest(ResourceManagerTestsBase):
    def test_list_with_include(self):
        application_id = ResourceId('1481211155')  # Banaan
        # application_id = ResourceId('1453997552')  # Testmagic
        app_store_versions, builds = self.api_client.app_store_versions.list_with_include(
            application_id,
            Build,
        )
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS
        assert len(app_store_versions) > 0
        for app_store_version in app_store_versions:
            assert isinstance(app_store_version, AppStoreVersion)
            assert app_store_version.type is ResourceType.APP_STORE_VERSIONS

    def test_read(self):
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        app_store_version = self.api_client.app_store_versions.read(app_store_version_id)
        assert isinstance(app_store_version, AppStoreVersion)
        assert app_store_version.id == app_store_version_id

    def test_read_app_store_version_submission(self):
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        app_store_version_submission = self.api_client.app_store_versions.read_app_store_version_submission(
            app_store_version_id,
        )
        assert isinstance(app_store_version_submission, AppStoreVersionSubmission)
        assert app_store_version_submission.id == '409ebefb-ebd1-4f1a-903d-6ba16e013ebf'

    def test_create(self):
        app_id = ResourceId('1481211155')
        build_id = ResourceId('650e6f10-5310-4533-a213-090f35436279')
        app_store_version = self.api_client.app_store_versions.create(
            Platform.IOS,
            '2.0.149',
            app_id,
            build_id,
        )
        assert isinstance(app_store_version, AppStoreVersion)

    def test_delete(self):
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        self.api_client.app_store_versions.delete(app_store_version_id)

    def test_read_build(self):
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        build = self.api_client.app_store_versions.read_build(app_store_version_id)
        assert isinstance(build, Build)
        assert build.id == ResourceId('9d967d5e-4946-432f-a111-1fd94949820b')

    def test_list_app_store_version_localizations(self):
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        app_store_version_localizations = \
            self.api_client.app_store_versions.list_app_store_version_localizations(app_store_version_id)
        for app_store_version_localization in app_store_version_localizations:
            assert isinstance(app_store_version_localization, AppStoreVersionLocalization)
            print(app_store_version_localization.json())
