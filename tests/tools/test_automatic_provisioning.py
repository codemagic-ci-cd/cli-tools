from __future__ import annotations

import argparse
import os
import pathlib
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from codemagic_cli_tools.tools.automatic_provisioning import AutomaticProvisioning
from codemagic_cli_tools.tools.automatic_provisioning import AutomaticProvisioningArgument
from codemagic_cli_tools.tools.automatic_provisioning import IssuerIdArgument
from codemagic_cli_tools.tools.automatic_provisioning import KeyIdentifierArgument
from codemagic_cli_tools.tools.automatic_provisioning import PrivateKeyArgument
from codemagic_cli_tools.tools.automatic_provisioning import PrivateKeyPathArgument


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in AutomaticProvisioning.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture()
def namespace_kwargs():
    ns_kwars = {
        AutomaticProvisioningArgument.ISSUER_ID.key: IssuerIdArgument('issuer-id'),
        AutomaticProvisioningArgument.KEY_IDENTIFIER.key: KeyIdentifierArgument('key-identifier'),
        AutomaticProvisioningArgument.PRIVATE_KEY.key: PrivateKeyArgument('-----BEGIN PRIVATE KEY-----'),
        AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key: None,
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
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key] = None
    _test_missing_argument(AutomaticProvisioningArgument.PRIVATE_KEY, namespace_kwargs)


@pytest.mark.parametrize('argument', [
    AutomaticProvisioningArgument.ISSUER_ID,
    AutomaticProvisioningArgument.KEY_IDENTIFIER,
])
@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_missing_arg_from_env(MockApiClient, namespace_kwargs, argument):
    namespace_kwargs[argument.key] = None

    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    os.environ[argument.value.type.environment_variable_key] = 'environment-value'

    _ = AutomaticProvisioning.from_cli_args(cli_args)
    api_client_args = MockApiClient.call_args[1]
    client_kwarg = api_client_args[argument.key]
    assert isinstance(client_kwarg, argument.type.argument_type)
    assert client_kwarg == argument.type.argument_type('environment-value')


def test_private_key_and_private_key_path_given(namespace_kwargs):
    with NamedTemporaryFile() as tf:
        namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key] = pathlib.Path(tf.name)
        cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
        with pytest.raises(argparse.ArgumentError) as exception_info:
            AutomaticProvisioning.from_cli_args(cli_args)
        message = str(exception_info.value)
        assert AutomaticProvisioningArgument.PRIVATE_KEY.key.upper() in message
        assert AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key.upper() in message
        assert AutomaticProvisioningArgument.PRIVATE_KEY.flags[0] in message


def test_private_key_invalid_path(namespace_kwargs):
    os.environ[PrivateKeyPathArgument.environment_variable_key] = 'this-is-not-a-file'
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key] = None
    namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
    cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
    with pytest.raises(ValueError) as exception_info:
        AutomaticProvisioning.from_cli_args(cli_args)
    assert 'this-is-not-a-file' in str(exception_info.value)


@pytest.mark.parametrize('configure_variable', [
    lambda argument, filename, ns_kwargs: os.environ.update(
        {argument.type.environment_variable_key: filename}),
    lambda argument, filename, ns_kwargs: ns_kwargs.update(
        {argument.key: PrivateKeyPathArgument(pathlib.Path(filename))})
])
@mock.patch('codemagic_cli_tools.tools.automatic_provisioning.AppStoreConnectApiClient')
def test_private_key_path_arg(MockApiClient, configure_variable, namespace_kwargs):
    pk = '-----BEGIN PRIVATE KEY-----\n...'
    with NamedTemporaryFile(mode='w') as tf:
        tf.write(pk)
        tf.flush()
        argument = AutomaticProvisioningArgument.PRIVATE_KEY_PATH
        namespace_kwargs[AutomaticProvisioningArgument.PRIVATE_KEY.key] = None
        configure_variable(argument, tf.name, namespace_kwargs)

        cli_args = argparse.Namespace(**{k: v for k, v in namespace_kwargs.items()})
        _ = AutomaticProvisioning.from_cli_args(cli_args)
        api_client_args = MockApiClient.call_args[1]
        client_kwarg = api_client_args['private_key']
        assert isinstance(client_kwarg, str)
        assert client_kwarg == pk
