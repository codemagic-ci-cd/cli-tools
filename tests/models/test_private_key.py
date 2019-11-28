from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import NamedTuple, Optional

import OpenSSL
import pytest

from models import PrivateKey


class PEM(NamedTuple):
    content: bytes
    public_key: bytes
    key_size: int
    password: Optional[bytes] = None


@lru_cache()
def _get_pem(filename: str, password: str = '') -> PEM:
    mocks_dir = pathlib.Path(__file__).parent / 'mocks'
    pem_path = mocks_dir / filename
    pub_key_path = mocks_dir / f'{filename}.pub'
    return PEM(pem_path.read_bytes(), pub_key_path.read_bytes(), 4096, password.encode())


def _encrypted_pem() -> PEM:
    return _get_pem('encrypted.pem', 'strong password')


def _unencrypted_pem() -> PEM:
    return _get_pem('unencrypted.pem')


@pytest.fixture
def encrypted_pem() -> PEM:
    return _encrypted_pem()


@pytest.fixture
def unencrypted_pem() -> PEM:
    return _unencrypted_pem()


@pytest.fixture(params=[_encrypted_pem(), _unencrypted_pem()])
def pem(request):
    return request.param


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
