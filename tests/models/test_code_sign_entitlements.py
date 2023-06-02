import pathlib
import shutil

import pytest

from codemagic.models import CodeSignEntitlements

_expected_entitlements = {
    'application-identifier': 'X8NNQ9CYL2.io.codemagic.capybara',
    'com.apple.developer.team-identifier': 'X8NNQ9CYL2',
    'get-task-allow': True,
    'keychain-access-groups': [
        'X8NNQ9CYL2.io.codemagic.capybara',
    ],
}


@pytest.mark.skipif(not shutil.which('codesign'), reason='Codesign not available')
def test_from_xcarchive(mock_xcarchive_path):
    entitlements = CodeSignEntitlements.from_xcarchive(mock_xcarchive_path)
    assert entitlements.plist == _expected_entitlements


@pytest.mark.skipif(not shutil.which('codesign'), reason='Codesign not available')
def test_from_ipa(mock_ipa_path):
    entitlements = CodeSignEntitlements.from_ipa(mock_ipa_path)
    assert entitlements.plist == _expected_entitlements


@pytest.mark.parametrize(
    'defined_environments_number, expected_environments',
    [
        (0, []),
        (1, ['Production']),
        (2, ['Development', 'Production']),
    ],
)
def test_get_icloud_container_environments(defined_environments_number, expected_environments):
    mock_filename = f'mock_{defined_environments_number}_icloud_container_environments.plist'
    mock_path = pathlib.Path(__file__).parent / 'mocks' / mock_filename
    entitlements = CodeSignEntitlements.from_plist(mock_path.read_bytes())
    assert entitlements.get_icloud_container_environments() == expected_environments
