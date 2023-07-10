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
    return pathlib.Path(__file__).parent / "mocks" / "AuthKeyMock.p8"


@pytest.fixture()
def namespace_kwargs(mock_auth_key):
    args = AppStoreConnectArgument
    ns_kwargs = {
        "action": "list-devices",
        args.CERTIFICATES_DIRECTORY.key: args.CERTIFICATES_DIRECTORY.get_default(),
        args.PROFILES_DIRECTORY.key: args.PROFILES_DIRECTORY.get_default(),
        args.LOG_REQUESTS.key: True,
        args.JSON_OUTPUT.key: False,
        args.ISSUER_ID.key: Types.IssuerIdArgument("issuer-id"),
        args.KEY_IDENTIFIER.key: Types.KeyIdentifierArgument("key-identifier"),
        args.PRIVATE_KEY.key: Types.PrivateKeyArgument(mock_auth_key.read_text()),
        args.UNAUTHORIZED_REQUEST_RETRIES.key: 1,
        args.SERVER_ERROR_RETRIES.key: 1,
        args.DISABLE_JWT_CACHE.key: True,
    }
    for arg in AppStoreConnect.CLASS_ARGUMENTS:
        if not hasattr(arg.type, "environment_variable_key"):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwargs
