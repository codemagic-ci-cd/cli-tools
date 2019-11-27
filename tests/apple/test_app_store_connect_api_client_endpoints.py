import uuid

import pytest

from apple.resources import App
from apple.resources import BundleId
from apple.resources import BundleIdCapability
from apple.resources import BundleIdPlatform
from apple.resources import CapabilityType
from apple.resources import LinkedResourceData
from apple.resources import Profile
from apple.resources import ResourceId
from apple.resources import ResourceType


CAPYBARA_ID = ResourceId('F88J43FA9J')


@pytest.mark.skip
def test_list_apps(api_client, _logger):
    apps = api_client.list_apps()
    assert len(apps) > 0
    for app in apps:
        assert isinstance(app, App)
        assert app.type is ResourceType.APP


@pytest.mark.skip
def test_register_bundle_id(api_client, _logger):
    bundle_id = api_client.register_bundle_id(
        'com.example.test-app',
        'com example test app',
        BundleIdPlatform.IOS
    )
    assert isinstance(bundle_id, BundleId)


@pytest.mark.skip
def test_modify_bundle_id(api_client, _logger):
    new_name = f'io codemagic capybara {uuid.uuid4()}'
    modified_bundle_id = api_client.modify_bundle_id(CAPYBARA_ID, name=new_name)
    assert isinstance(modified_bundle_id, BundleId)
    assert modified_bundle_id.attributes.name == new_name


@pytest.mark.skip
def test_delete_bundle_id(api_client, _logger):
    api_client.delete_bundle_id(ResourceId('US2AH335HU'))


@pytest.mark.skip
def test_list_bundle_ids(api_client, _logger):
    bundle_ids = api_client.list_bundle_ids()
    assert len(bundle_ids) > 0
    for bundle_id in bundle_ids:
        assert isinstance(bundle_id, BundleId)
        assert bundle_id.type is ResourceType.BUNDLE_ID


@pytest.mark.skip
def test_read_bundle_id(api_client, _logger):
    bundle_id = api_client.read_bundle_id(CAPYBARA_ID)
    assert isinstance(bundle_id, BundleId)
    assert bundle_id.attributes.name.startswith('io codemagic capybara')


@pytest.mark.skip
def test_list_bundle_id_profile_ids(api_client, _logger):
    linked_profiles = api_client.list_bundle_id_profile_ids(CAPYBARA_ID)
    assert len(linked_profiles) > 0
    for linked_profile in linked_profiles:
        assert isinstance(linked_profile, LinkedResourceData)
        assert linked_profile.type is ResourceType.PROFILES


@pytest.mark.skip
def test_list_bundle_id_profiles(api_client, _logger):
    profiles = api_client.list_bundle_id_profiles(CAPYBARA_ID)
    assert len(profiles) > 0
    for profile in profiles:
        assert isinstance(profile, Profile)
        assert profile.type is ResourceType.PROFILES


@pytest.mark.skip
def test_list_bundle_id_capabilility_ids(api_client, _logger):
    linked_capabilities = api_client.list_bundle_id_capabilility_ids(CAPYBARA_ID)
    assert len(linked_capabilities) > 0
    for capability in linked_capabilities:
        assert isinstance(capability, LinkedResourceData)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES


@pytest.mark.skip
def test_list_bundle_id_capabilities(api_client, _logger):
    capabilities = api_client.list_bundle_id_capabilities(CAPYBARA_ID)
    assert len(capabilities) > 0
    for capability in capabilities:
        assert isinstance(capability, BundleIdCapability)
        assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES


@pytest.mark.skip
def test_enable_capability(api_client, _logger):
    capability_type = CapabilityType.ACCESS_WIFI_INFORMATION
    capability = api_client.enable_capability(capability_type, CAPYBARA_ID)
    assert isinstance(capability, BundleIdCapability)
    assert capability.type is ResourceType.BUNDLE_ID_CAPABILITIES
    assert capability.attributes.capabilityType is capability_type
    _logger.info(capability)


@pytest.mark.skip
def test_disable_capability(api_client, _logger):
    capability_id = ResourceId('F88J43FA9J_ACCESS_WIFI_INFORMATION')
    api_client.disable_capability(capability_id)
