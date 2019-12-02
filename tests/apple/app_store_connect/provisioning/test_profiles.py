import pytest

from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import Certificate
from codemagic_cli_tools.apple.resources import Device
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import Profile
from codemagic_cli_tools.apple.resources import ProfileType
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
class ProfilesTest(ResourceManagerTestsBase):

    def test_create(self):
        name = 'test profile'
        profile_type = ProfileType.IOS_APP_DEVELOPMENT
        bundle_id_resource_id = ResourceId('F88J43FA9J')
        certificate_id = ResourceId('29NU422CRF')
        device_ids = [ResourceId('D9PW3SW6K2'), ResourceId('8UCFZA68RK')]
        profile = self.api_client.profiles.create(
            name=name,
            profile_type=profile_type,
            bundle_id=bundle_id_resource_id,
            certificates=[certificate_id],
            devices=device_ids,
        )
        assert isinstance(profile, Profile)
        assert profile.attributes.name == name
        assert profile.attributes.profileType is profile_type

    def test_delete(self):
        profile_id = ResourceId('ZK3RZ4B465')
        self.api_client.profiles.delete(profile_id)

    def test_list(self):
        profiles = self.api_client.profiles.list()
        assert len(profiles) > 0
        for profile in profiles:
            assert isinstance(profile, Profile)
            assert profile.type is ResourceType.PROFILES

    def test_read(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        profile = self.api_client.profiles.read(profile_id)
        assert isinstance(profile, Profile)
        assert profile.id == profile_id
        assert profile.type is ResourceType.PROFILES

    def test_read_bundle_id(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        bundle_id = self.api_client.profiles.read_bundle_id(profile_id)
        assert isinstance(bundle_id, BundleId)
        assert bundle_id.type is ResourceType.BUNDLE_ID

    def test_get_bundle_id_resource_id(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        bundle_id = self.api_client.profiles.get_bundle_id_resource_id(profile_id)
        assert isinstance(bundle_id, LinkedResourceData)
        assert bundle_id.type is ResourceType.BUNDLE_ID

    def test_list_certificates(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        certificates = self.api_client.profiles.list_certificates(profile_id)
        assert len(certificates) > 0
        for certificate in certificates:
            assert isinstance(certificate, Certificate)
            assert certificate.type is ResourceType.CERTIFICATES

    def test_list_certificate_ids(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        certificates = self.api_client.profiles.list_certificate_ids(profile_id)
        assert len(certificates) > 0
        for certificate in certificates:
            assert isinstance(certificate, LinkedResourceData)
            assert certificate.type is ResourceType.CERTIFICATES

    def test_list_devices(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        devices = self.api_client.profiles.list_devices(profile_id)
        assert len(devices) > 0
        for device in devices:
            assert isinstance(device, Device)
            assert device.type is ResourceType.DEVICES

    def test_list_device_ids(self):
        profile_id = ResourceId('M7GU3HQ8CZ')
        devices = self.api_client.profiles.list_device_ids(profile_id)
        assert len(devices) > 0
        for device in devices:
            assert isinstance(device, LinkedResourceData)
            assert device.type is ResourceType.DEVICES
