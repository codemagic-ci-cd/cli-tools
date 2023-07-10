import os

import pytest
from codemagic.apple.resources import Build
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId

from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get("RUN_LIVE_API_TESTS"), reason="Live App Store Connect API access")
class PreReleaseVersionsTest(ResourceManagerTestsBase):
    def test_list(self):
        versions_filter = self.api_client.pre_release_versions.Filter(app=ResourceId("1481211155"))
        pre_release_versions = self.api_client.pre_release_versions.list(resource_filter=versions_filter)
        assert isinstance(pre_release_versions, list)
        assert len(pre_release_versions) > 0
        for pre_release_version in pre_release_versions:
            assert isinstance(pre_release_version, PreReleaseVersion)

    def test_list_build_for_pre_release_version(self):
        pre_release_version_id = ResourceId("fa63f894-f00f-4f87-adc0-2949fa032a84")
        builds = self.api_client.pre_release_versions.list_builds(pre_release_version_id)
        assert isinstance(builds, list)
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
