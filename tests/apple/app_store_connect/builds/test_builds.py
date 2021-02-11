import os
import pytest
from unittest import mock

from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildOrdering
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.parametrize('ordering, reverse, expected_ordering', [
    (BuildOrdering.VERSION, False, 'version'),
    (BuildOrdering.UPLOADED_DATE, True, '-uploadedDate'),
])
def test_ordering(ordering, reverse, expected_ordering, api_client):
    with mock.patch.object(api_client.builds.client, 'paginate', return_value=[]) as mock_paginate:
        builds = api_client.builds.list(ordering=ordering, reverse=reverse)
        mock_paginate.assert_called_once_with(mock.ANY, params={'sort': expected_ordering})


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BuildsTest(ResourceManagerTestsBase):
    def test_list(self):
        builds = self.api_client.builds.list()
        assert len(builds) > 0
        for build in builds:
            assert isinstance(build, Build)
            assert build.type is ResourceType.BUILDS

    def test_read(self):
        BUILD_ID = ResourceId('d2f965a4-7b0f-46c5-a086-6435a92676b5')
        build = self.api_client.builds.read(BUILD_ID)
        assert isinstance(build, Build)
        assert build.attributes.version == '3'
