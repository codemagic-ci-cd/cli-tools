from __future__ import annotations

import argparse
import os
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from codemagic_cli_tools.tools.automatic_provisioning import AutomaticProvisioning
from codemagic_cli_tools.tools.provisioning.automatic_provisioning_arguments import AutomaticProvisioningArgument
from codemagic_cli_tools.tools.provisioning.automatic_provisioning_arguments import Types


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in AutomaticProvisioning.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture()
def namespace_kwargs():
    ns_kwars = {
        AutomaticProvisioningArgument.CERTIFICATES_DIRECTORY.key: AutomaticProvisioningArgument.CERTIFICATES_DIRECTORY.get_default(),
        AutomaticProvisioningArgument.PROFILES_DIRECTORY.key: AutomaticProvisioningArgument.PROFILES_DIRECTORY.get_default(),
        AutomaticProvisioningArgument.LOG_REQUESTS.key: True,
        AutomaticProvisioningArgument.JSON_OUTPUT.key: False,
        AutomaticProvisioningArgument.ISSUER_ID.key: Types.IssuerIdArgument('issuer-id'),
        AutomaticProvisioningArgument.KEY_IDENTIFIER.key: Types.KeyIdentifierArgument('key-identifier'),
        AutomaticProvisioningArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument('-----BEGIN PRIVATE KEY-----'),
    }
    for arg in AutomaticProvisioning.CLASS_ARGUMENTS:
        if not hasattr(arg.type, 'environment_variable_key'):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwars


def _test_missing_argument(argument, _namespace_kwargs):
    cli_args = argparse.Namespace(**{k: v for k, v in _namespace_kwargs.items()})
    with pytest.raises(argparse.ArgumentError) as exception_info:
        AutomaticProvisioning.from_cli_args(cli_args)
    message = str(exception_info.value)
    assert argument.key.upper() in message
    assert argument.type.environment_variable_key in message
    assert ','.join(argument.flags) in message


@pytest.mark.parametrize('argument', [
    AutomaticProvisioningArgument.ISSUER_ID,
    AutomaticProvisioningArgument.KEY_IDENTIFIER,
    AutomaticProvisioningArgument.PRIVATE_KEY,
])
def test_missing_arg(cli_argument_group, namespace_kwargs, argument):
    namespace_kwargs[argument.key] = None
    _test_missing_argument(argument, namespace_kwargs)


def test_missing_private_key_arg(namespace_kwargs):
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
    _test_missing_argument(AutomaticProvisioningArgument.PRIVATE_KEY, namespace_kwargs)


@pytest.mark.parametrize('argument, api_client_arg_index', [
    (AutomaticProvisioningArgument.KEY_IDENTIFIER, 0),
    (AutomaticProvisioningArgument.ISSUER_ID, 1),
])
@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_missing_arg_from_env(MockApiClient, namespace_kwargs, argument, api_client_arg_index):
    namespace_kwargs[argument.key] = None

    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    os.environ[argument.value.type.environment_variable_key] = 'environment-value'

    _ = AutomaticProvisioning.from_cli_args(cli_args)
    api_client_args = MockApiClient.call_args[0]
    client_arg = api_client_args[api_client_arg_index]
    assert isinstance(client_arg, argument.type.argument_type)
    assert client_arg == argument.type.argument_type('environment-value')


def test_private_key_invalid_path(namespace_kwargs):
    os.environ[Types.PrivateKeyArgument.environment_variable_key] = '@file:this-is-not-a-file'
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    with pytest.raises(argparse.ArgumentTypeError) as exception_info:
        AutomaticProvisioning.from_cli_args(cli_args)
    assert 'this-is-not-a-file' in str(exception_info.value)


@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_read_private_key(MockApiClient, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = Types.PrivateKeyArgument(pk)
    _do_private_key_assertions(pk, MockApiClient, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda filename, ns_kwargs: os.environ.update(
        {AutomaticProvisioningArgument.PRIVATE_KEY.type.environment_variable_key: f'@file:{filename}'}),
    lambda filename, ns_kwargs: ns_kwargs.update(
        {AutomaticProvisioningArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument(f'@file:{filename}')})
])
@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_private_key_path_arg(MockApiClient, configure_variable, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    with NamedTemporaryFile(mode='w') as tf:
        tf.write(pk)
        tf.flush()
        namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
        configure_variable(tf.name, namespace_kwargs)
        _do_private_key_assertions(pk, MockApiClient, namespace_kwargs)


@pytest.mark.parametrize('configure_variable', [
    lambda ns_kwargs: os.environ.update(
        {AutomaticProvisioningArgument.PRIVATE_KEY.type.environment_variable_key: '@env:PK_VALUE'}),
    lambda ns_kwargs: ns_kwargs.update(
        {AutomaticProvisioningArgument.PRIVATE_KEY.key: Types.PrivateKeyArgument(f'@env:PK_VALUE')})
])
@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_private_key_env_arg(MockApiClient, configure_variable, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    os.environ['PK_VALUE'] = pk
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
    configure_variable(namespace_kwargs)
    _do_private_key_assertions(pk, MockApiClient, namespace_kwargs)


def _do_private_key_assertions(private_key_value, moc_api_client, cli_namespace):
    cli_args = argparse.Namespace(**{k: v for k, v in cli_namespace.items()})
    _ = AutomaticProvisioning.from_cli_args(cli_args)
    _, _, private_key_arg = moc_api_client.call_args[0]
    assert isinstance(private_key_arg, str)
    assert private_key_arg == private_key_value
