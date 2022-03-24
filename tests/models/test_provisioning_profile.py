from datetime import datetime
from datetime import timezone

import pytest

from codemagic.models import ProvisioningProfile


@pytest.fixture
def provisioning_profile(mock_provisioning_profile_path):
    return ProvisioningProfile.from_path(mock_provisioning_profile_path)


@pytest.mark.parametrize('profile_name', [
    'iOS Team Provisioning Profile: io.codemagic.app.debug',
    'iOS Team Ad Hoc Provisioning Profile: io.codemagic.app.ad-hoc',
    'iOS Team Store Provisioning Profile: io.codemagic.app.store',
])
def test_is_xcode_managed_profile(profile_name):
    assert ProvisioningProfile.is_xcode_managed(profile_name)


@pytest.mark.parametrize('profile_name', [
    '',
    'io codemagic app development',
    'iOS Team Profile: App Store',
])
def test_is_not_xcode_managed_profile(profile_name):
    assert ProvisioningProfile.is_xcode_managed(profile_name) is False


def test_profile_creation_date(provisioning_profile):
    expected_created_date = datetime(2022, 3, 24, 10, 2, 42, tzinfo=timezone.utc)
    assert provisioning_profile.creation_date == expected_created_date


def test_profile_expiration_date(provisioning_profile):
    expected_expiration_date = datetime(2023, 3, 24, 10, 2, 42, tzinfo=timezone.utc)
    assert provisioning_profile.expiration_date == expected_expiration_date
