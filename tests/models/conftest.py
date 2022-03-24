import pathlib
from typing import Dict
from typing import Union

import pytest


@pytest.fixture
def _models_mocks_dir():
    return pathlib.Path(__file__).parent / 'mocks'


@pytest.fixture
def mock_ipa_path(_models_mocks_dir):
    return _models_mocks_dir / 'mock.ipa'


@pytest.fixture
def mock_certificate_p12(_models_mocks_dir):
    return _models_mocks_dir / 'certificate.p12'


@pytest.fixture
def mock_certificate_p12_no_password(_models_mocks_dir):
    return _models_mocks_dir / 'certificate-no-password.p12'


@pytest.fixture
def mock_xcarchive_path(_models_mocks_dir):
    return _models_mocks_dir / 'mock.xcarchive'


@pytest.fixture
def export_options_list_path(_models_mocks_dir) -> pathlib.Path:
    return _models_mocks_dir / 'export_options.plist'


@pytest.fixture
def export_options_list_bytes(export_options_list_path) -> bytes:
    return export_options_list_path.read_bytes()


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


@pytest.fixture
def mock_provisioning_profile_path(_models_mocks_dir):
    return _models_mocks_dir / 'codemagic_io_wildcard_development.mobileprovision'
