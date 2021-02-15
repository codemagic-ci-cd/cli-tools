import os
import pytest
from unittest import mock

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
