from __future__ import annotations

import pytest

from codemagic_cli_tools.models import PrivateKey


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
    pk = PrivateKey.from_pem(unencrypted_pem.content, b'wrong password')
    # Unencrypted keys can be opened with any password
    assert pk.rsa_key.key_size == unencrypted_pem.key_size
