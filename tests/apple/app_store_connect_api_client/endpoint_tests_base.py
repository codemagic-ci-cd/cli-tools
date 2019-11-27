import logging
import unittest

import pytest

from apple.app_store_connect_api import AppStoreConnectApiClient


@pytest.mark.usefixtures('class_api_client', 'class_logger')
class EndpointTestsBase(unittest.TestCase):
    api_client: AppStoreConnectApiClient
    logger: logging.Logger
