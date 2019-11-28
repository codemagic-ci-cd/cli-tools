import logging
import os
import pathlib
import sys
from functools import lru_cache
from typing import Optional, NamedTuple

import pytest

from apple.app_store_connect_api import AppStoreConnectApiClient
from apple.app_store_connect_api import IssuerId
from apple.app_store_connect_api import KeyIdentifier


class PEM(NamedTuple):
    content: bytes
    public_key: bytes
    key_size: int
    password: Optional[bytes] = None


@lru_cache()
def _get_pem(filename: str, password: str = '', key_size: int = 2048) -> PEM:
    mocks_dir = pathlib.Path(__file__).parent / 'mocks'
    pem_path = mocks_dir / filename
    pub_key_path = mocks_dir / f'{filename}.pub'
    return PEM(
        pem_path.read_bytes().rstrip(b'\n'),
        pub_key_path.read_bytes().rstrip(b'\n'),
        key_size,
        password.encode())


def _encrypted_pem() -> PEM:
    return _get_pem('encrypted.pem', 'strong password')


def _unencrypted_pem() -> PEM:
    return _get_pem('unencrypted.pem')


@lru_cache()
def _api_client() -> AppStoreConnectApiClient:
    key_path = pathlib.Path(os.environ['TEST_APPLE_PRIVATE_KEY_PATH'])
    return AppStoreConnectApiClient(
        KeyIdentifier(os.environ['TEST_APPLE_KEY_IDENTIFIER']),
        IssuerId(os.environ['TEST_APPLE_ISSUER_ID']),
        key_path.expanduser().read_text())


def _logger():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    requests_logger = logging.getLogger('requests')
    requests_logger.addHandler(handler)
    requests_logger.setLevel(logging.ERROR)
    return logger


@pytest.fixture
def api_client() -> AppStoreConnectApiClient:
    return _api_client()


@pytest.fixture(scope='class')
def class_api_client(request):
    request.cls.api_client = _api_client()


@pytest.fixture
def logger() -> logging.Logger:
    return _logger()


@pytest.fixture(scope='class')
def class_logger(request):
    logger = _logger()
    logger.debug(f'Attach logger to {request.cls.__name__}')
    request.cls.logger = logger


@pytest.fixture
def encrypted_pem() -> PEM:
    return _encrypted_pem()


@pytest.fixture(scope='class')
def class_encrypted_pem(request):
    request.cls.encrypted_pem = _encrypted_pem()


@pytest.fixture
def unencrypted_pem() -> PEM:
    return _unencrypted_pem()


@pytest.fixture(scope='class')
def class_unencrypted_pem(request):
    request.cls.unencrypted_pem = _unencrypted_pem()


@pytest.fixture(params=[_encrypted_pem(), _unencrypted_pem()])
def pem(request):
    return request.param
