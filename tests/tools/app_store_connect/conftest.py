from __future__ import annotations

import os
import pathlib

import pytest

from codemagic.tools.app_store_connect import AppStoreConnect
from codemagic.tools.app_store_connect import AppStoreConnectArgument
from codemagic.tools.app_store_connect import Types


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in AppStoreConnect.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture
def mock_auth_key() -> pathlib.Path:
    return pathlib.Path(__file__).parent / 'mocks' / 'AuthKeyMock.p8'


@pytest.fixture()
def namespace_kwargs(mock_auth_key):
    ns_kwargs = {
        'action': 'list-devices',
        AppStoreConnectArgument.CERTIFICATES_DIRECTORY.key:
            AppStoreConnectArgument.CERTIFICATES_DIRECTORY.get_default(),
        AppStoreConnectArgument.PROFILES_DIRECTORY.key: AppStoreConnectArgument.PROFILES_DIRECTORY.get_default(),
        AppStoreConnectArgument.LOG_REQUESTS.key: True,
        AppStoreConnectArgument.JSON_OUTPUT.key: False,
        AppStoreConnectArgument.ISSUER_ID.key: Types.IssuerIdArgument('issuer-id'),
        AppStoreConnectArgument.KEY_IDENTIFIER.key: Types.KeyIdentifierArgument('key-identifier'),
        AppStoreConnectArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument(mock_auth_key.read_text()),
        AppStoreConnectArgument.UNAUTHORIZED_REQUEST_RETRIES.key: 1,
        AppStoreConnectArgument.SERVER_ERROR_RETRIES.key: 1,
        AppStoreConnectArgument.DISABLE_JWT_CACHE.key: True,
    }
    for arg in AppStoreConnect.CLASS_ARGUMENTS:
        if not hasattr(arg.type, 'environment_variable_key'):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwargs
