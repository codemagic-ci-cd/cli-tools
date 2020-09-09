import pytest

from codemagic.models import CodeSignEntitlements

_expected_entitlements = {
    "application-identifier": "X8NNQ9CYL2.io.codemagic.capybara",
    "com.apple.developer.team-identifier": "X8NNQ9CYL2",
    "get-task-allow": True,
    "keychain-access-groups": [
        "X8NNQ9CYL2.io.codemagic.capybara"
    ]
}


@pytest.mark.skip(reason='Codesign not available')
def test_from_xcarchive(mock_xcarchive_path):
    entitlements = CodeSignEntitlements.from_xcarchive(mock_xcarchive_path)
    assert entitlements.plist == _expected_entitlements


@pytest.mark.skip(reason='Codesign not available')
def test_from_ipa(mock_ipa_path):
    entitlements = CodeSignEntitlements.from_ipa(mock_ipa_path)
    assert entitlements.plist == _expected_entitlements
