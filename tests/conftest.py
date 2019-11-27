import logging
import os
import pathlib
import sys

import pytest

from apple.app_store_connect_api import AppStoreConnectApiClient
from apple.app_store_connect_api import IssuerId
from apple.app_store_connect_api import KeyIdentifier


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
