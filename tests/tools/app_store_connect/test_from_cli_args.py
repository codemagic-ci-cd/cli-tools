from __future__ import annotations

import argparse
import os
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from codemagic.tools.app_store_connect import AppStoreConnect
from codemagic.tools.app_store_connect import AppStoreConnectArgument
from codemagic.tools.app_store_connect import Types


def _test_missing_argument(argument, _namespace_kwargs):
    cli_args = argparse.Namespace(**{k: v for k, v in _namespace_kwargs.items()})
    with pytest.raises(argparse.ArgumentError) as exception_info:
        _ = AppStoreConnect.from_cli_args(cli_args).api_client
    message = str(exception_info.value)
    assert argument.key.upper() in message
    assert argument.type.environment_variable_key in message
    assert ','.join(argument.flags) in message


@pytest.mark.parametrize('argument', [
    AppStoreConnectArgument.ISSUER_ID,
    AppStoreConnectArgument.KEY_IDENTIFIER,
    AppStoreConnectArgument.PRIVATE_KEY,
])
def test_missing_arg(cli_argument_group, namespace_kwargs, argument):
    namespace_kwargs[argument.key] = None
    _test_missing_argument(argument, namespace_kwargs)


def test_missing_private_key_arg(namespace_kwargs):
    namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = None
    _test_missing_argument(AppStoreConnectArgument.PRIVATE_KEY, namespace_kwargs)


@pytest.mark.parametrize('argument, api_client_arg_index', [
    (AppStoreConnectArgument.KEY_IDENTIFIER, 0),
    (AppStoreConnectArgument.ISSUER_ID, 1),
])
@mock.patch('codemagic.tools.app_store_connect.AppStoreConnectApiClient')
def test_missing_arg_from_env(mock_appstore_api_client, namespace_kwargs, argument, api_client_arg_index):
    namespace_kwargs[argument.key] = None

    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    os.environ[argument.value.type.environment_variable_key] = 'environment-value'

    _ = AppStoreConnect.from_cli_args(cli_args).api_client
    api_client_args = mock_appstore_api_client.call_args[0]
    client_arg = api_client_args[api_client_arg_index]
    assert isinstance(client_arg, argument.type.argument_type)
    assert client_arg == argument.type.argument_type('environment-value')


def test_invalid_private_key_from_env(namespace_kwargs):
    os.environ[Types.PrivateKeyArgument.environment_variable_key] = 'this is not a private key'
    namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = None
    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    with pytest.raises(argparse.ArgumentTypeError) as exception_info:
        AppStoreConnect.from_cli_args(cli_args)
    assert 'this is not a private key' in str(exception_info.value)


def test_private_key_invalid_path(namespace_kwargs):
    os.environ[Types.PrivateKeyArgument.environment_variable_key] = '@file:this-is-not-a-file'
    namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = None
    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    with pytest.raises(argparse.ArgumentTypeError) as exception_info:
        AppStoreConnect.from_cli_args(cli_args)
    assert 'this-is-not-a-file' in str(exception_info.value)


@mock.patch('codemagic.tools.app_store_connect.AppStoreConnectApiClient')
def test_read_private_key(mock_appstore_api_client, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = Types.PrivateKeyArgument(pk)
    _do_private_key_assertions(pk, mock_appstore_api_client, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda filename, ns_kwargs: os.environ.update(
        {AppStoreConnectArgument.PRIVATE_KEY.type.environment_variable_key: f'@file:{filename}'}),
    lambda filename, ns_kwargs: ns_kwargs.update(
        {AppStoreConnectArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument(f'@file:{filename}')}),
])
@mock.patch('codemagic.tools.app_store_connect.AppStoreConnectApiClient')
def test_private_key_path_arg(mock_appstore_api_client, configure_variable, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    with NamedTemporaryFile(mode='w') as tf:
        tf.write(pk)
        tf.flush()
        namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = None
        configure_variable(tf.name, namespace_kwargs)
        _do_private_key_assertions(pk, mock_appstore_api_client, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda ns_kwargs: os.environ.update(
        {AppStoreConnectArgument.PRIVATE_KEY.type.environment_variable_key: '@env:PK_VALUE'}),
    lambda ns_kwargs: ns_kwargs.update(
        {AppStoreConnectArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument('@env:PK_VALUE')}),
])
@mock.patch('codemagic.tools.app_store_connect.AppStoreConnectApiClient')
def test_private_key_env_arg(mock_appstore_api_client, configure_variable, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    os.environ['PK_VALUE'] = pk
    namespace_kwargs[AppStoreConnectArgument.PRIVATE_KEY.key] = None
    configure_variable(namespace_kwargs)
    _do_private_key_assertions(pk, mock_appstore_api_client, namespace_kwargs)


def _do_private_key_assertions(private_key_value, moc_appstore_api_client, cli_namespace):
    cli_args = argparse.Namespace(**cli_namespace)
    _ = AppStoreConnect.from_cli_args(cli_args).api_client
    _, _, private_key_arg = moc_appstore_api_client.call_args[0]
    assert isinstance(private_key_arg, str)
    assert private_key_arg == private_key_value
