from __future__ import annotations

import argparse
import os
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from codemagic.tools.google_play import GooglePlay
from codemagic.tools.google_play import GooglePlayArgument
from codemagic.tools.google_play import Types

credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in GooglePlay.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture()
def namespace_kwargs():
    ns_kwargs = {
        credentials_argument.key: Types.CredentialsArgument('{"type":"service_account"}'),
        GooglePlayArgument.PACKAGE_NAME.key: Types.PackageName('package.name'),
        GooglePlayArgument.LOG_REQUESTS.key: False,
        GooglePlayArgument.JSON_OUTPUT.key: False,
    }
    for arg in GooglePlay.CLASS_ARGUMENTS:
        if not hasattr(arg.type, 'environment_variable_key'):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwargs


def _test_missing_argument(argument, _namespace_kwargs):
    cli_args = argparse.Namespace(**dict(_namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    message = str(exception_info.value)
    assert argument.key.upper() in message
    if hasattr(argument.type, 'environment_variable_key'):
        assert argument.type.environment_variable_key in message
    assert ','.join(argument.flags) in message


@pytest.mark.parametrize('argument', [
    credentials_argument,
    GooglePlayArgument.PACKAGE_NAME,
])
def test_missing_arg(cli_argument_group, namespace_kwargs, argument):
    namespace_kwargs[argument.key] = None
    _test_missing_argument(argument, namespace_kwargs)


def test_missing_creedentials_arg(namespace_kwargs):
    namespace_kwargs[credentials_argument.key] = None
    _test_missing_argument(credentials_argument, namespace_kwargs)


def test_invalid_credentials_from_env(namespace_kwargs):
    os.environ[Types.CredentialsArgument.environment_variable_key] = 'invalid credentials'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: Provided value "invalid credentials" is not valid'


def test_credentials_invalid_path(namespace_kwargs):
    os.environ[Types.CredentialsArgument.environment_variable_key] = '@file:this-is-not-a-file'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: File "this-is-not-a-file" does not exist'


@mock.patch('codemagic.tools.google_play.GooglePlayDeveloperAPIClient')
def test_read_private_key(mock_google_play_api_client, namespace_kwargs):
    credentials = '{"type":"service_account"}'
    namespace_kwargs[credentials_argument.key] = Types.CredentialsArgument(credentials)
    _do_credentials_assertions(credentials, mock_google_play_api_client, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda filename, ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: f'@file:{filename}'}),
    lambda filename, ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: Types.CredentialsArgument(f'@file:{filename}')}),
])
@mock.patch('codemagic.tools.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_path_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    credentials = '{"type":"service_account"}'
    with NamedTemporaryFile(mode='w') as tf:
        tf.write(credentials)
        tf.flush()
        namespace_kwargs[credentials_argument.key] = None
        configure_variable(tf.name, namespace_kwargs)
        _do_credentials_assertions(credentials, mock_google_play_api_client, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: '@env:CREDENTIALS'}),
    lambda ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: Types.CredentialsArgument('@env:CREDENTIALS')}),
])
@mock.patch('codemagic.tools.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_env_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    credentials = '{"type":"service_account"}'
    os.environ['CREDENTIALS'] = credentials
    namespace_kwargs[credentials_argument.key] = None
    configure_variable(namespace_kwargs)
    _do_credentials_assertions(credentials, mock_google_play_api_client, namespace_kwargs)


def _do_credentials_assertions(credentials_value, moc_google_play_api_client, cli_namespace):
    cli_args = argparse.Namespace(**dict(cli_namespace.items()))
    _ = GooglePlay.from_cli_args(cli_args)
    credentials_arg, _, _ = moc_google_play_api_client.call_args[0]
    print(type(credentials_arg))
    assert isinstance(credentials_arg, str)
    assert credentials_arg == credentials_value
