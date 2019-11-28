from __future__ import annotations

import OpenSSL
import pytest

from models import PrivateKey


def test_get_public_key(pem):
    rsa_key = PrivateKey.pem_to_rsa(pem.content, pem.password)
    public_key = rsa_key.public_key()
    assert pem.public_key == PrivateKey.get_public_key(public_key)


def test_pem_to_rsa_with_encrypted_key_wrong_password(encrypted_pem):
    with pytest.raises(OpenSSL.crypto.Error) as exception_info:
        PrivateKey.pem_to_rsa(encrypted_pem.content, b'wrong password')
    error = exception_info.value
    assert 'bad decrypt' in error.args[0][0]


def test_pem_to_rsa_with_unencrypted_key_wrong_password(unencrypted_pem):
    rsa_key = PrivateKey.pem_to_rsa(unencrypted_pem.content, b'wrong password')
    # Unencrypted keys can be opened with any password
    assert rsa_key.key_size == unencrypted_pem.key_size
