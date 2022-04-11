from __future__ import annotations

import argparse
import os
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from codemagic.tools.google_play import GooglePlay
from codemagic.tools.google_play.argument_types import CredentialsArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument

credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in GooglePlay.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture()
def namespace_kwargs():
    ns_kwargs = {
        credentials_argument.key: CredentialsArgument('{"type":"service_account"}'),
    }
    for arg in GooglePlay.CLASS_ARGUMENTS:
        if not hasattr(arg.type, 'environment_variable_key'):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwargs


def test_missing_credentials_arg(namespace_kwargs):
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))

    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)

    message = str(exception_info.value)
    assert credentials_argument.key.upper() in message
    if hasattr(credentials_argument.type, 'environment_variable_key'):
        assert credentials_argument.type.environment_variable_key in message
    assert ','.join(credentials_argument.flags) in message


def test_invalid_credentials_from_env(namespace_kwargs):
    os.environ[CredentialsArgument.environment_variable_key] = 'invalid credentials'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: Provided value "invalid credentials" is not valid'


def test_credentials_invalid_path(namespace_kwargs):
    os.environ[CredentialsArgument.environment_variable_key] = '@file:this-is-not-a-file'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: File "this-is-not-a-file" does not exist'


@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_read_private_key(mock_google_play_api_client, namespace_kwargs):
    namespace_kwargs[credentials_argument.key] = CredentialsArgument('{"type":"service_account"}')
    _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
    mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')


@pytest.mark.parametrize('configure_variable', [
    lambda filename, ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: f'@file:{filename}'},
    ),
    lambda filename, ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: CredentialsArgument(f'@file:{filename}')},
    ),
])
@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_path_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    with NamedTemporaryFile(mode='w') as tf:
        tf.write('{"type":"service_account"}')
        tf.flush()
        namespace_kwargs[credentials_argument.key] = None
        configure_variable(tf.name, namespace_kwargs)

        _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
        mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')


@pytest.mark.parametrize('configure_variable', [
    lambda ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: '@env:CREDENTIALS'},
    ),
    lambda ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: CredentialsArgument('@env:CREDENTIALS')},
    ),
])
@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_env_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    os.environ['CREDENTIALS'] = '{"type":"service_account"}'
    namespace_kwargs[credentials_argument.key] = None
    configure_variable(namespace_kwargs)

    _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
    mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')
