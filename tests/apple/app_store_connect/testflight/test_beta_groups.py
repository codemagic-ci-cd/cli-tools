import os

import pytest

from codemagic.apple.app_store_connect import AppStoreConnectApiError
from codemagic.apple.app_store_connect.testflight import BetaGroups
from codemagic.apple.resources import ResourceId
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class TestBetaGroups(ResourceManagerTestsBase):

    def test_list(self):
        beta_groups = self.api_client.beta_groups.list()
        assert len(beta_groups) >= 1

    def test_list_with_filter(self):
        app = ResourceId('1496105355')
        name = 'Codemagic CLI Tools test'
        resource_filter = BetaGroups.Filter(app=app, name=name)
        beta_groups = self.api_client.beta_groups.list(resource_filter)
        beta_group = beta_groups[0]

        assert len(beta_groups) == 1
        assert beta_group.attributes.name == name
        assert beta_group.attributes.isInternalGroup is False
        assert beta_group.attributes.hasAccessToAllBuilds is None

    def test_list_with_filter_for_internal_group(self):
        app = ResourceId('1496105355')

        internal_beta_group_name = 'App\xa0Store Connect Users'
        resource_filter = BetaGroups.Filter(app=app, name=internal_beta_group_name)
        beta_groups = self.api_client.beta_groups.list(resource_filter)
        beta_group = beta_groups[0]

        assert len(beta_groups) == 1
        assert beta_group.attributes.name == 'App\xa0Store Connect Users'
        assert beta_group.attributes.isInternalGroup is True
        assert beta_group.attributes.hasAccessToAllBuilds is True

    def test_add_build_to_beta_groups(self):
        build = ResourceId('02c602b8-f7e5-4a72-8f16-fd34500fb43a')
        beta_group = ResourceId('c954ae49-625e-49cc-a8eb-3dbf8aff94c9')

        self.api_client.beta_groups.add_build(beta_group, build)

    def test_remove_build_from_beta_groups(self):
        build = ResourceId('02c602b8-f7e5-4a72-8f16-fd34500fb43a')
        beta_group = ResourceId('c954ae49-625e-49cc-a8eb-3dbf8aff94c9')

        self.api_client.beta_groups.remove_build(beta_group, build)

    def test_add_if_build_does_not_exist(self):
        build = ResourceId('00000000-0000-0000-0000-000000000000')
        beta_group = ResourceId('c954ae49-625e-49cc-a8eb-3dbf8aff94c9')

        with pytest.raises(AppStoreConnectApiError):
            self.api_client.beta_groups.add_build(beta_group, build)
