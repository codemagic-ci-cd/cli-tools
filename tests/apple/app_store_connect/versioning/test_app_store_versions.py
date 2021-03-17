import os

import pytest

from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BuildsTest(ResourceManagerTestsBase):
    def test_list(self):
        app_store_versions, builds = self.api_client.app_store_versions.list_with_include(
            ResourceId('1453997552'), Build)
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS
        assert len(app_store_versions) > 0
        for app_store_version in app_store_versions:
            assert isinstance(app_store_version, AppStoreVersion)
            assert app_store_version.type is ResourceType.APP_STORE_VERSIONS
