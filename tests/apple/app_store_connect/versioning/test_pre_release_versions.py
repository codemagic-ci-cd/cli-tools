import os
import pytest

from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


APPLICATION_ID = '1453997552'

@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BuildsTest(ResourceManagerTestsBase):
    def test_list(self):
        resource_filter = self.api_client.pre_release_versions.Filter(app=APPLICATION_ID)
        pre_release_versions, builds = self.api_client.pre_release_versions.list(resource_filter=resource_filter)
        builds = self.api_client.builds.list()
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS
        assert len(pre_release_versions) > 0
        for pre_release_version in pre_release_versions:
            assert isinstance(pre_release_version, PreReleaseVersion)
            assert pre_release_version.type is ResourceType.PRE_RELEASE_VERSIONS
