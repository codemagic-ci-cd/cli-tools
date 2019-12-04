#!/usr/bin/env python3

from __future__ import annotations

import argparse
import enum
import os
import pathlib

from codemagic_cli_tools import cli
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from .base_provisioning import BaseProvisioning


class AutomaticProvisioningError(cli.CliAppException):
    pass


class KeyIdentifierArgument(cli.EnvironmentArgumentValue[KeyIdentifier]):
    argument_type = KeyIdentifier


class IssuerIdArgument(cli.EnvironmentArgumentValue[IssuerId]):
    argument_type = IssuerId


class PrivateKeyArgument(cli.EnvironmentArgumentValue[str]):
    @classmethod
    def _is_valid(cls, raw_value: str) -> bool:
        return raw_value.startswith('-----BEGIN PRIVATE KEY-----')


class DefaultEnvironmentKeys(enum.Enum):
    ISSUER_ID = 'APP_STORE_CONNECT_ISSUER_ID'
    KEY_IDENTIFIER = 'APP_STORE_CONNECT_KEY_IDENTIFIER'
    PRIVATE_KEY = 'APP_STORE_CONNECT_PRIVATE_KEY'
    PRIVATE_KEY_PATH = 'APP_STORE_CONNECT_PRIVATE_KEY_PATH'


class AutomaticProvisioningArgument(cli.Argument):
    ISSUER_ID = cli.ArgumentProperties(
        key='issuer_id',
        flags=('--issuer-id',),
        type=IssuerIdArgument,
        description=' '.join([
            'App Store Connect API Key Issuer ID.',
            'Identifies the issuer who created the authentication token.',
            f'If not given, the value will be checked from environment variable '
            f'`{DefaultEnvironmentKeys.ISSUER_ID.value}`.',
            f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        ]),
        argparse_kwargs={'required': False},
    )
    KEY_IDENTIFIER = cli.ArgumentProperties(
        key='key_identifier',
        flags=('--key-id',),
        type=KeyIdentifierArgument,
        description=' '.join([
            'App Store Connect API Key ID.',
            f'If not given, the value will be checked from environment variable '
            f'`{DefaultEnvironmentKeys.KEY_IDENTIFIER.value}`.',
            f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        ]),
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY = cli.ArgumentProperties(
        key='private_key',
        flags=('--private-key',),
        type=PrivateKeyArgument,
        description=' '.join([
            'App Store Connect API private key.',
            'Can be used in place of `PRIVATE_KEY_PATH`.',
            f'If not given, the value will be checked from environment variable '
            f'`{DefaultEnvironmentKeys.PRIVATE_KEY.value}`.',
            f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        ]),
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY_PATH = cli.ArgumentProperties(
        key='private_key_path',
        flags=('--private-key-path',),
        type=pathlib.Path,
        description=' '.join([
            'Path to the App Store Connect API private key.',
            'Can be used in place of `PRIVATE_KEY`.',
            f'If not given, the value will be checked from environment variable '
            f'`{DefaultEnvironmentKeys.PRIVATE_KEY_PATH.value}`.',
            f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        ]),
        argparse_kwargs={'required': False},
    )
    BUNDLE_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_identifier',
        flags=('--bundle-identifier',),
        description='Bundle identifier for which the signing files will be downloaded',
        argparse_kwargs={'required': True},
    )


@cli.common_arguments(
    AutomaticProvisioningArgument.ISSUER_ID,
    AutomaticProvisioningArgument.KEY_IDENTIFIER,
    AutomaticProvisioningArgument.PRIVATE_KEY,
    AutomaticProvisioningArgument.PRIVATE_KEY_PATH,
)
class AutomaticProvisioning(BaseProvisioning):
    """
    Utility to download code signing certificates and provisioning profiles
    from Apple Developer Portal using App Store Connect API to perform iOS code signing.
    """

    def __init__(self, key_identifier: KeyIdentifier, issuer_id: IssuerId, private_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_client = AppStoreConnectApiClient(
            key_identifier,
            issuer_id,
            private_key)

    @classmethod
    def _get_private_key_argument(cls, cli_args: argparse.Namespace) -> str:
        private_key = AutomaticProvisioningArgument.PRIVATE_KEY.from_args(cli_args)
        private_key_path = AutomaticProvisioningArgument.PRIVATE_KEY_PATH.from_args(cli_args)
        env_private_key = os.environ.get(DefaultEnvironmentKeys.PRIVATE_KEY.value)
        env_private_key_path = os.environ.get(DefaultEnvironmentKeys.PRIVATE_KEY_PATH.value)

        if private_key and private_key_path:
            AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error(
                f'`Both {AutomaticProvisioningArgument.PRIVATE_KEY.key.upper()}` and '
                f'`{AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key.upper()}` were given. Choose only one.')

        if private_key:
            return private_key.value
        if private_key_path:
            return private_key_path.read_text()
        if env_private_key:
            return env_private_key
        if env_private_key_path:
            return pathlib.Path(env_private_key_path).read_text()

        AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error(
            f'Either `{AutomaticProvisioningArgument.PRIVATE_KEY.key.upper()}` argument, '
            f'`{AutomaticProvisioningArgument.PRIVATE_KEY_PATH.key.upper()}` argument, '
            f'`{DefaultEnvironmentKeys.PRIVATE_KEY_PATH.value}` environment variable'
            f'or `{DefaultEnvironmentKeys.PRIVATE_KEY.value}` environment variable has to be specified.')

    @classmethod
    def _get_issuer_id_argument(cls, cli_args: argparse.Namespace) -> IssuerId:
        issuer_id = AutomaticProvisioningArgument.ISSUER_ID.from_args(cli_args)
        environment_issuer_id = os.environ.get(DefaultEnvironmentKeys.ISSUER_ID.value)

        if issuer_id:
            return issuer_id.value
        if environment_issuer_id:
            return IssuerId(environment_issuer_id)
        AutomaticProvisioningArgument.ISSUER_ID.raise_argument_error(
            f'Either `{AutomaticProvisioningArgument.ISSUER_ID.key.upper()}` argument '
            f'or `{DefaultEnvironmentKeys.ISSUER_ID.value}` environment variable has to be specified.')

    @classmethod
    def _get_key_identifier_argument(cls, cli_args: argparse.Namespace) -> KeyIdentifier:
        key_identifier = AutomaticProvisioningArgument.KEY_IDENTIFIER.from_args(cli_args)
        environment_key_identifier = os.environ.get(DefaultEnvironmentKeys.KEY_IDENTIFIER.value)

        if key_identifier:
            return key_identifier.value
        if environment_key_identifier:
            return KeyIdentifier(environment_key_identifier)

        AutomaticProvisioningArgument.KEY_IDENTIFIER.raise_argument_error(
            f'Either `{AutomaticProvisioningArgument.KEY_IDENTIFIER.key.upper()}` argument '
            f'or `{DefaultEnvironmentKeys.KEY_IDENTIFIER.value}` environment variable has to be specified.')

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        return AutomaticProvisioning(
            issuer_id=cls._get_issuer_id_argument(cli_args),
            key_identifier=cls._get_key_identifier_argument(cli_args),
            private_key=cls._get_private_key_argument(cli_args),
        )

    @cli.action('fetch', AutomaticProvisioningArgument.BUNDLE_IDENTIFIER)
    def fetch(self, bundle_identifier: str):
        """
        Fetch code signing files from Apple Developer portal for
        specified bundle identifier
        """
        # TODO Apple Developer Portal communication

    @cli.action('get-identifier', AutomaticProvisioningArgument.BUNDLE_IDENTIFIER)
    def get_or_create_bundle_id(self, bundle_identifier: str, create: bool = False):
        """
        Find specified bundle identifier from Apple Developer portal.
        """
        bundle_id_filter = self.api_client.bundle_ids.Filter(identifier=bundle_identifier)
        self.api_client.bundle_ids.list(bundle_id_filter=bundle_id_filter)


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
