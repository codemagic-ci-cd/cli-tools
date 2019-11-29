import pytest

from apple.resources import Profile
from apple.resources import ResourceType
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
class ProfileOperationsTest(OperationsTestsBase):

    def test_list_profiles(self):
        profiles = self.api_client.profiles.list()
        assert len(profiles) > 0
        for profile in profiles:
            assert isinstance(profile, Profile)
            assert profile.type is ResourceType.PROFILES
