import pytest

from apple.resources import BundleId, Certificate
from apple.resources import LinkedResourceData
from apple.resources import Profile
from apple.resources import ResourceId
from apple.resources import ResourceType
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
class ProfileOperationsTest(OperationsTestsBase):

    def test_create(self):
        ...

    def test_delete(self):
        ...

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
        ...

    def test_list_device_ids(self):
        ...
