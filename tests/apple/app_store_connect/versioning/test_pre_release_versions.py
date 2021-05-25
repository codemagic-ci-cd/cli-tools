import os

import pytest

from codemagic.apple.resources import Build
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class PreReleaseVersionsTest(ResourceManagerTestsBase):
    def test_list(self):
        resource_filter = self.api_client.pre_release_versions.Filter(app=ResourceId('1453997552'))
        pre_release_versions, builds = self.api_client.pre_release_versions.list_with_include(
            Build, resource_filter=resource_filter)
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS
        assert len(pre_release_versions) > 0
        for pre_release_version in pre_release_versions:
            assert isinstance(pre_release_version, PreReleaseVersion)
            assert pre_release_version.type is ResourceType.PRE_RELEASE_VERSIONS
