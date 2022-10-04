from __future__ import annotations

import base64
import hashlib
import pathlib

import pytest

from codemagic.models import PrivateKey


def test_get_public_key(pem):
    pk = PrivateKey.from_pem(pem.content, pem.password)
    assert pem.public_key == pk.get_public_key()


def test_private_key_invalid_key(pem):
    with pytest.raises(ValueError) as exception_info:
        PrivateKey.from_pem(pem.content + b'not a good suffix', pem.password)
    error = exception_info.value
    assert str(error) == 'Invalid private key PEM content'


def test_pem_to_rsa_with_encrypted_key_wrong_password(encrypted_pem):
    with pytest.raises(ValueError) as exception_info:
        PrivateKey.from_pem(encrypted_pem.content, b'wrong password')
    error = exception_info.value
    assert str(error) == 'Invalid private key passphrase'


def test_pem_to_rsa_with_unencrypted_key_wrong_password(unencrypted_pem):
    with pytest.raises(ValueError) as exception_info:
        PrivateKey.from_pem(unencrypted_pem.content, b'wrong password')
    error = exception_info.value
    assert str(error) == 'Invalid private key passphrase'


@pytest.mark.parametrize(
    'mock_file_name, expected_fingerprint', [
        ('mock_rsa_private_key', 'fb8ca2f11c34fcfb01332256d138cfd1'),
        ('mock_openssh_private_key', '9c34c3684fccaaaf5e706bb65158ac1a'),
    ],
)
def test_load_private_key_from_buffer(mock_file_name, expected_fingerprint):
    rsa_path = pathlib.Path(__file__).parent / 'mocks' / mock_file_name
    pk = PrivateKey.from_buffer(rsa_path.read_text())
    public_key_content = pk.get_public_key().split()[1]
    key_bytes = base64.b64decode(public_key_content)
    fingerprint = hashlib.md5(key_bytes).hexdigest()
    assert fingerprint == expected_fingerprint


@pytest.mark.parametrize(
    'mock_p12_name, password, expected_fingerprint', [
        ('certificate.p12', '123456', '16764b6fe08edf6ebba22e68f6f95b40'),
        ('certificate-no-password.p12', None, '16764b6fe08edf6ebba22e68f6f95b40'),
    ],
)
def test_load_private_key_from_p12(mock_p12_name, password, expected_fingerprint):
    p12_path = pathlib.Path(__file__).parent / 'mocks' / mock_p12_name
    pk = PrivateKey.from_p12(p12_path.read_bytes(), password)
    public_key_content = pk.get_public_key().split()[1]
    key_bytes = base64.b64decode(public_key_content)
    fingerprint = hashlib.md5(key_bytes).hexdigest()
    assert fingerprint == expected_fingerprint
