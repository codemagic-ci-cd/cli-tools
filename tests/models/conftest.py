import pathlib
from typing import Dict
from typing import Union

import pytest


def _export_options_plist_path():
    return pathlib.Path(__file__).parent / 'mocks' / 'export_options.plist'


@pytest.fixture
def mock_ipa_path():
    return pathlib.Path(__file__).parent / 'mocks' / 'mock.ipa'


@pytest.fixture
def mock_certificate_p12():
    return pathlib.Path(__file__).parent / 'mocks' / 'certificate.p12'


@pytest.fixture
def mock_certificate_p12_no_password():
    return pathlib.Path(__file__).parent / 'mocks' / 'certificate-no-password.p12'


@pytest.fixture
def mock_xcarchive_path():
    return pathlib.Path(__file__).parent / 'mocks' / 'mock.xcarchive'


@pytest.fixture
def export_options_list_path() -> pathlib.Path:
    return _export_options_plist_path()


@pytest.fixture
def export_options_list_bytes() -> bytes:
    path = _export_options_plist_path()
    return path.read_bytes()


@pytest.fixture
def export_options_dict() -> Dict[str, Union[bool, str, Dict[str, str]]]:
    return {
        'method': 'development',
        'provisioningProfiles': {
            'io.codemagic.capybara': 'io codemagic capybara development 1555086834',
        },
        'signingCertificate': 'iPhone Developer',
        'signingStyle': 'manual',
        'teamID': 'X8NNQ9CYL2',
        'uploadBitcode': False,
        'uploadSymbols': False,
    }
