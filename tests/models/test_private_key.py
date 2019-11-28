from __future__ import annotations

import pathlib
from typing import NamedTuple, Optional

import pytest

from models import PrivateKey


class PEM(NamedTuple):
    content: bytes
    password: Optional[bytes] = None


@pytest.fixture
def encrypted_pem() -> PEM:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'encrypted.pem'
    return PEM(mock_path.read_bytes(), b'strong password')


@pytest.fixture
def unencrypted_pem() -> PEM:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'unencrypted.pem'
    return PEM(mock_path.read_bytes())


def test_pem_to_rsa_with_encrypted_key(encrypted_pem):
    rsa_key = PrivateKey.pem_to_rsa(encrypted_pem.content, encrypted_pem.password)
    # TODO


def test_pem_to_rsa_with_unencrypted_key(unencrypted_pem):
    rsa_key = PrivateKey.pem_to_rsa(unencrypted_pem.content)
    # TODO
