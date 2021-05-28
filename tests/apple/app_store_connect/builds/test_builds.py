import os

import pytest

from codemagic.apple.resources import Build
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


@pytest.mark.parametrize('python_field_name, apple_filter_name', [
    ('processing_state', 'processingState'),
    ('version', 'version'),
    ('pre_release_version_version', 'preReleaseVersion.version'),
])
def test_builds_filter(app_store_connect_api_client, python_field_name, apple_filter_name):
    get_apple_filter_name = app_store_connect_api_client.builds.Filter._get_field_name
    assert get_apple_filter_name(python_field_name) == apple_filter_name
