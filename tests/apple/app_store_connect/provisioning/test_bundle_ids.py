import os
import uuid

import pytest

from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdCapability
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase

CAPYBARA_ID = ResourceId('F88J43FA9J')


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BundleIdsTest(ResourceManagerTestsBase):

    def test_create(self):
        bundle_id = self.api_client.bundle_ids.create(
            'com.example.test-app',
            'com example test app',
            BundleIdPlatform.IOS,
        )
        assert isinstance(bundle_id, BundleId)

    def test_modify(self):
        new_name = f'io codemagic capybara {uuid.uuid4()}'
        modified_bundle_id = self.api_client.bundle_ids.modify(CAPYBARA_ID, name=new_name)
        assert isinstance(modified_bundle_id, BundleId)
        assert modified_bundle_id.attributes.name == new_name

    def test_delete(self):
        self.api_client.bundle_ids.delete(ResourceId('US2AH335HU'))

    def test_list_identifier_and_platform_constraint(self):
        expected_identifier = 'io.codemagic.banaan'
        expected_platform = BundleIdPlatform.IOS
        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=expected_identifier,
            platform=expected_platform,
        )
        bundle_ids = self.api_client.bundle_ids.list(resource_filter=bundle_id_filter)
        assert len(bundle_ids) == 2
        for bundle_id in bundle_ids:
            assert isinstance(bundle_id, BundleId)
            assert bundle_id.type is ResourceType.BUNDLE_ID
            assert expected_identifier in bundle_id.attributes.identifier
            assert bundle_id.attributes.platform in (expected_platform, BundleIdPlatform.UNIVERSAL)

    def test_list(self):
        bundle_ids = self.api_client.bundle_ids.list()
        assert len(bundle_ids) > 0
        for bundle_id in bundle_ids:
            assert isinstance(bundle_id, BundleId)
            assert bundle_id.type is ResourceType.BUNDLE_ID

    def test_read(self):
        bundle_id = self.api_client.bundle_ids.read(CAPYBARA_ID)
        assert isinstance(bundle_id, BundleId)
        assert bundle_id.attributes.name.startswith('io codemagic capybara')

    def test_list_profile_ids(self):
        linked_profiles = self.api_client.bundle_ids.list_profile_ids(CAPYBARA_ID)
        assert len(linked_profiles) > 0
        for linked_profile in linked_profiles:
            assert isinstance(linked_profile, LinkedResourceData)
            assert linked_profile.type is ResourceType.PROFILES

    def test_list_profiles(self):
        profiles = self.api_client.bundle_ids.list_profiles(CAPYBARA_ID)
        assert len(profiles) > 0
        for profile in profiles:
            assert isinstance(profile, Profile)
            assert profile.type is ResourceType.PROFILES

    def test_list_capabilility_ids(self):
        linked_capabilities = self.api_client.bundle_ids.list_capabilility_ids(CAPYBARA_ID)
        assert len(linked_capabilities) > 0
        for capability in linked_capabilities:
            assert isinstance(capability, LinkedResourceData)
            assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES

    def test_list_capabilities(self):
        capabilities = self.api_client.bundle_ids.list_capabilities(CAPYBARA_ID)
        assert len(capabilities) > 0
        for capability in capabilities:
            assert isinstance(capability, BundleIdCapability)
            assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
