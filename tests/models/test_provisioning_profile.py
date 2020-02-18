import pytest

from codemagic.models import ProvisioningProfile


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
