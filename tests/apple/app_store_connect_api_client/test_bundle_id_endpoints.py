import unittest
import uuid

import pytest

from apple.resources import BundleId
from apple.resources import BundleIdCapability
from apple.resources import BundleIdPlatform
from apple.resources import LinkedResourceData
from apple.resources import Profile
from apple.resources import ResourceId
from apple.resources import ResourceType

CAPYBARA_ID = ResourceId('F88J43FA9J')


@pytest.mark.skip(reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_api_client', 'class_logger')
class BundleIdEndpointsTest(unittest.TestCase):

    def test_register_bundle_id(self):
        bundle_id = self.api_client.register_bundle_id(
            'com.example.test-app',
            'com example test app',
            BundleIdPlatform.IOS
        )
        assert isinstance(bundle_id, BundleId)

    def test_modify_bundle_id(self):
        new_name = f'io codemagic capybara {uuid.uuid4()}'
        modified_bundle_id = self.api_client.modify_bundle_id(CAPYBARA_ID, name=new_name)
        assert isinstance(modified_bundle_id, BundleId)
        assert modified_bundle_id.attributes.name == new_name

    def test_delete_bundle_id(self):
        self.api_client.delete_bundle_id(ResourceId('US2AH335HU'))

    def test_list_bundle_ids(self):
        bundle_ids = self.api_client.list_bundle_ids()
        assert len(bundle_ids) > 0
        for bundle_id in bundle_ids:
            assert isinstance(bundle_id, BundleId)
            assert bundle_id.type is ResourceType.BUNDLE_ID

    def test_read_bundle_id(self):
        bundle_id = self.api_client.read_bundle_id(CAPYBARA_ID)
        assert isinstance(bundle_id, BundleId)
        assert bundle_id.attributes.name.startswith('io codemagic capybara')

    def test_list_bundle_id_profile_ids(self):
        linked_profiles = self.api_client.list_bundle_id_profile_ids(CAPYBARA_ID)
        assert len(linked_profiles) > 0
        for linked_profile in linked_profiles:
            assert isinstance(linked_profile, LinkedResourceData)
            assert linked_profile.type is ResourceType.PROFILES

    def test_list_bundle_id_profiles(self):
        profiles = self.api_client.list_bundle_id_profiles(CAPYBARA_ID)
        assert len(profiles) > 0
        for profile in profiles:
            assert isinstance(profile, Profile)
            assert profile.type is ResourceType.PROFILES

    def test_list_bundle_id_capabilility_ids(self):
        linked_capabilities = self.api_client.list_bundle_id_capabilility_ids(CAPYBARA_ID)
        assert len(linked_capabilities) > 0
        for capability in linked_capabilities:
            assert isinstance(capability, LinkedResourceData)
            assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES

    def test_list_bundle_id_capabilities(self):
        capabilities = self.api_client.list_bundle_id_capabilities(CAPYBARA_ID)
        assert len(capabilities) > 0
        for capability in capabilities:
            assert isinstance(capability, BundleIdCapability)
            assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
