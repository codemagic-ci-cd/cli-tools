from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import shutil
import sys
from functools import lru_cache
from typing import NamedTuple
from typing import Optional

import pytest

from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient
from codemagic.utilities import log

log.initialize_logging(
    stream=open(os.devnull, 'w'),
    verbose=False,
    enable_logging=False,
)


class PEM(NamedTuple):
    content: bytes
    public_key: bytes
    key_size: int
    password: Optional[bytes] = None


@lru_cache()
def _get_pem(filename: str, password: Optional[str] = None, key_size: int = 2048) -> PEM:
    mocks_dir = pathlib.Path(__file__).parent / 'mocks'
    pem_path = mocks_dir / filename
    pub_key_path = mocks_dir / f'{filename}.pub'
    return PEM(
        pem_path.read_bytes().rstrip(b'\n'),
        pub_key_path.read_bytes().rstrip(b'\n'),
        key_size,
        password.encode() if password is not None else None,
    )


def _encrypted_pem() -> PEM:
    return _get_pem('encrypted.pem', 'strong password')


def _unencrypted_pem() -> PEM:
    return _get_pem('unencrypted.pem')


@lru_cache()
def _appstore_api_client() -> AppStoreConnectApiClient:
    if 'TEST_APPLE_PRIVATE_KEY_PATH' in os.environ:
        key_path = pathlib.Path(os.environ['TEST_APPLE_PRIVATE_KEY_PATH'])
        private_key = key_path.expanduser().read_text()
        key_identifier = os.environ['TEST_APPLE_KEY_IDENTIFIER']
        issuer_id = os.environ['TEST_APPLE_ISSUER_ID']
    elif 'TEST_APPLE_PRIVATE_KEY_CONTENT' in os.environ:
        private_key = os.environ['TEST_APPLE_PRIVATE_KEY_CONTENT']
        key_identifier = os.environ['TEST_APPLE_KEY_IDENTIFIER']
        issuer_id = os.environ['TEST_APPLE_ISSUER_ID']
    else:
        _logger().warning('Using mock App Store Connect private key')
        private_key = (
            '-----BEGIN PRIVATE KEY-----\n'
            'MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgg57UZZvJPP2RSVnb\n'
            'z09v3WoH9SPgoZW9Aa9zLVAIVQGgCgYIKoZIzj0DAQehRANCAAQOmjqG2uAvOmx3\n'
            '8cXoNHDaAD9aDiNDqG2LcsOloIKgBRTLwcQPkTd/emZZndx0a0gDtviu2UDQ4l2/\n'
            'ngq1dJ3d\n'
            '-----END PRIVATE KEY-----\n'
        )
        key_identifier = '6NMHPUB3G8'
        issuer_id = 'def71228-a8db-74ca-792d-763bded762de'  # Random non functional issuer

    return AppStoreConnectApiClient(
        KeyIdentifier(key_identifier),
        IssuerId(issuer_id),
        private_key,
    )


@lru_cache(1)
def _google_play_api_credentials() -> dict:
    if 'TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_PATH' in os.environ:
        credentials_path = pathlib.Path(os.environ['TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_PATH'])
        credentials = credentials_path.expanduser().read_text()
    elif 'TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_CONTENT' in os.environ:
        credentials = os.environ['TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_CONTENT']
    else:
        raise KeyError(
            'TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_PATH',
            'TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_CONTENT',
        )
    return json.loads(credentials)


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
def app_store_api_client() -> AppStoreConnectApiClient:
    return _appstore_api_client()


@pytest.fixture
def google_play_api_client() -> GooglePlayDeveloperAPIClient:
    credentials = _google_play_api_credentials()
    return GooglePlayDeveloperAPIClient(credentials)


@pytest.fixture(scope='class')
def class_appstore_api_client(request):
    request.cls.api_client = _appstore_api_client()


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


@pytest.fixture
def certificate_asn1() -> bytes:
    mocks_dir = pathlib.Path(__file__).parent / 'mocks'
    asn1_path = mocks_dir / 'certificate.asn1'
    return asn1_path.read_bytes()


@pytest.fixture(scope='class')
def class_unencrypted_pem(request):
    request.cls.unencrypted_pem = _unencrypted_pem()


@pytest.fixture(params=[_encrypted_pem(), _unencrypted_pem()])
def pem(request):
    return request.param


@pytest.fixture
def cli_argument_group():
    parser = argparse.ArgumentParser()
    action_parsers = parser.add_subparsers()
    action_parser = action_parsers.add_parser('action parser')
    return action_parser.add_argument_group()


@pytest.fixture()
def temp_dir(tmpdir) -> pathlib.Path:
    yield pathlib.Path(tmpdir)
    if not os.environ.get('CI'):
        # Cleanup generated dirs if not running on CI
        shutil.rmtree(tmpdir)
