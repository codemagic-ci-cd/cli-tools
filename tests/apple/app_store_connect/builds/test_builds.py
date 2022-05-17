import os

import pytest

from codemagic.apple.app_store_connect.builds import Builds
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BuildsTest(ResourceManagerTestsBase):
    def test_list(self):
        builds = self.api_client.builds.list()
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS

    def test_read(self):
        build_id = ResourceId('650e6f10-5310-4533-a213-090f35436279')
        build = self.api_client.builds.read(build_id)
        assert isinstance(build, Build)
        assert build.id == build_id

    def test_read_app_store_version(self):
        build_id = ResourceId('352d5aca-e73e-4cbd-865f-ff64dae5db32')
        app_store_version = self.api_client.builds.read_app_store_version(build_id)
        assert isinstance(app_store_version, AppStoreVersion)
        assert app_store_version.id == '409ebefb-ebd1-4f1a-903d-6ba16e013ebf'

    def test_read_app_store_version_not_exists(self):
        build_id = ResourceId('3bf3e846-3d31-4e1e-ab0f-0834fb9f9a26')
        app_store_version = self.api_client.builds.read_app_store_version(build_id)
        assert app_store_version is None


@pytest.mark.parametrize('python_field_name, apple_filter_name', [
    ('processing_state', 'processingState'),
    ('version', 'version'),
    ('pre_release_version_version', 'preReleaseVersion.version'),
])
def test_builds_filter(python_field_name, apple_filter_name):
    get_apple_filter_name = Builds.Filter._get_field_name
    assert get_apple_filter_name(python_field_name) == apple_filter_name
