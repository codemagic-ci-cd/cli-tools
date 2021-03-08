import logging
import unittest

import pytest

from codemagic.apple.app_store_connect import AppStoreConnectApiClient


@pytest.mark.usefixtures('class_appstore_api_client', 'class_logger')
class ResourceManagerTestsBase(unittest.TestCase):
    api_client: AppStoreConnectApiClient
    logger: logging.Logger
