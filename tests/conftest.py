import logging
import os
import pathlib
import sys

import pytest

from apple.app_store_connect_api import AppStoreConnectApiClient
from apple.app_store_connect_api import IssuerId
from apple.app_store_connect_api import KeyIdentifier
from apple.resources import ResourceId


@pytest.fixture
def capybara_id() -> ResourceId:
    return ResourceId('F88J43FA9J')


@pytest.fixture
def key_identifier() -> KeyIdentifier:
    return KeyIdentifier(os.environ['TEST_APPLE_KEY_IDENTIFIER'])


@pytest.fixture
def issuer_id() -> IssuerId:
    return IssuerId(os.environ['TEST_APPLE_ISSUER_ID'])


@pytest.fixture
def api_private_key() -> str:
    key_path = pathlib.Path(os.environ['TEST_APPLE_PRIVATE_KEY_PATH'])
    return key_path.expanduser().read_text()


@pytest.fixture
def api_client(key_identifier, issuer_id, api_private_key) -> AppStoreConnectApiClient:
    return AppStoreConnectApiClient(key_identifier, issuer_id, api_private_key)


@pytest.fixture(autouse=False)
def _logger() -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    requests_logger = logging.getLogger('requests')
    requests_logger.addHandler(handler)
    requests_logger.setLevel(logging.ERROR)
    return logger
