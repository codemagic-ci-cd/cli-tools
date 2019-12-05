#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib

from codemagic_cli_tools import cli
from codemagic_cli_tools.apple import AppStoreConnectApiError
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from codemagic_cli_tools.apple.resources import BundleIdPlatform
from codemagic_cli_tools.cli.colors import Colors
from .base_provisioning import BaseProvisioning


class AutomaticProvisioningError(cli.CliAppException):
    pass


class IssuerIdArgument(cli.EnvironmentArgumentValue[IssuerId]):
    argument_type = IssuerId
    environment_variable_key = 'APP_STORE_CONNECT_ISSUER_ID'


class KeyIdentifierArgument(cli.EnvironmentArgumentValue[KeyIdentifier]):
    argument_type = KeyIdentifier
    environment_variable_key = 'APP_STORE_CONNECT_KEY_IDENTIFIER'


class PrivateKeyArgument(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY'
    alternative_to = 'PRIVATE_KEY_PATH'

    @classmethod
    def _is_valid(cls, value: str) -> bool:
        return value.startswith('-----BEGIN PRIVATE KEY-----')


class PrivateKeyPathArgument(cli.EnvironmentVariableDefaultArgumentValue[pathlib.Path]):
    environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY_PATH'
    alternative_to = 'PRIVATE_KEY'
    argument_type = pathlib.Path

    @classmethod
    def _is_valid(cls, value: pathlib.Path) -> bool:
        return value.exists() and value.is_file()


API_DOCS_REFERENCE = f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.'


class AutomaticProvisioningArgument(cli.Argument):
    LOG_REQUESTS = cli.ArgumentProperties(
        key='log_requests',
        flags=('--log-api-calls',),
        type=bool,
        description='Turn on logging for App Store Connect API HTTP requests',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    ISSUER_ID = cli.ArgumentProperties(
        key='issuer_id',
        flags=('--issuer-id',),
        type=IssuerIdArgument,
        description=f'App Store Connect API Key Issuer ID. Identifies the issuer '
                    f'who created the authentication token. {API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )
    KEY_IDENTIFIER = cli.ArgumentProperties(
        key='key_identifier',
        flags=('--key-id',),
        type=KeyIdentifierArgument,
        description=f'App Store Connect API Key ID. {API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY = cli.ArgumentProperties(
        key='private_key',
        flags=('--private-key',),
        type=PrivateKeyArgument,
        description=f'App Store Connect API private key. {API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY_PATH = cli.ArgumentProperties(
        key='private_key_path',
        flags=('--private-key-path',),
        type=PrivateKeyPathArgument,
        description=f'Path to the App Store Connect API private key. {API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )
    BUNDLE_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_identifier',
        description='Bundle identifier for which the signing files will be downloaded',
    )
    CREATE = cli.ArgumentProperties(
        key='create',
        flags=('--create',),
        type=bool,
        description='Whether to create the resource if id does not exist yet',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    PLATFORM = cli.ArgumentProperties(
        key='platform',
        flags=('--platform',),
        type=BundleIdPlatform,
        description='Bundle ID platform',
        argparse_kwargs={
            'required': False,
            'choices': list(BundleIdPlatform),
            'default': BundleIdPlatform.IOS,
        },
    )


@cli.common_arguments(
    AutomaticProvisioningArgument.LOG_REQUESTS,
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

    def __init__(self,
                 key_identifier: KeyIdentifier,
                 issuer_id: IssuerId,
                 private_key: str,
                 log_requests: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.api_client = AppStoreConnectApiClient(
            key_identifier=key_identifier,
            issuer_id=issuer_id,
            private_key=private_key,
            log_requests=log_requests,
        )

    @classmethod
    def _get_private_key(cls, cli_args: argparse.Namespace) -> str:
        private_key_argument = AutomaticProvisioningArgument.PRIVATE_KEY.from_args(cli_args)
        private_key_path_argument = AutomaticProvisioningArgument.PRIVATE_KEY_PATH.from_args(cli_args)
        if private_key_argument is None and private_key_path_argument is None:
            raise AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error()
        if private_key_argument is not None and private_key_path_argument is not None:
            arguments = (AutomaticProvisioningArgument.PRIVATE_KEY, AutomaticProvisioningArgument.PRIVATE_KEY_PATH)
            given_arguments = ' and '.join(map(lambda k: Colors.CYAN(k.key.upper()), arguments))
            raise AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error(
                f'Both {given_arguments} were given. Choose one.')

        if private_key_argument:
            return private_key_argument.value
        return private_key_path_argument.value.read_text()

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        key_identifier_argument = AutomaticProvisioningArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AutomaticProvisioningArgument.ISSUER_ID.from_args(cli_args)
        if issuer_id_argument is None:
            raise AutomaticProvisioningArgument.ISSUER_ID.raise_argument_error()
        if key_identifier_argument is None:
            raise AutomaticProvisioningArgument.KEY_IDENTIFIER.raise_argument_error()
        return AutomaticProvisioning(
            issuer_id=issuer_id_argument.value,
            key_identifier=key_identifier_argument.value,
            private_key=cls._get_private_key(cli_args),
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            log_requests=cli_args.log_requests,
        )

    @cli.action('fetch', AutomaticProvisioningArgument.BUNDLE_IDENTIFIER)
    def fetch(self, bundle_identifier: str):
        """
        Fetch code signing files from Apple Developer portal for
        specified bundle identifier
        """
        # TODO Apple Developer Portal communication

    @cli.action('get-identifier',
                AutomaticProvisioningArgument.BUNDLE_IDENTIFIER,
                AutomaticProvisioningArgument.CREATE,
                AutomaticProvisioningArgument.PLATFORM)
    def get_or_create_bundle_id(self,
                                bundle_identifier: str,
                                create: bool = False,
                                platform: BundleIdPlatform = BundleIdPlatform.IOS):
        """
        Find specified bundle identifier from Apple Developer portal.
        """

        bundle_id_filter = self.api_client.bundle_ids.Filter(identifier=bundle_identifier)
        try:
            bundle_ids = self.api_client.bundle_ids.list(bundle_id_filter=bundle_id_filter)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.logger.info(f'Found {len(bundle_ids)} Bundle IDs matching {bundle_id_filter.constraints()}')
        if not bundle_ids and not create:
            raise AutomaticProvisioningError(
                f'Did not find any bundle ids matching specified filters: {bundle_id_filter.constraints()}')

        if bundle_ids:
            bundle_id = bundle_ids[0]
            self.logger.info(f'Found Bundle ID {bundle_id}')
            return bundle_id

        self.logger.info(f'Bundle ID matching {bundle_id_filter.constraints()} not found.')
        name = bundle_identifier.replace('.', ' ')
        self.logger.info(f'Creating new Bundle ID "{bundle_identifier}" with name "{name}" for platform {platform}')
        try:
            bundle_id = self.api_client.bundle_ids.register(bundle_identifier, name, platform)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))
        self.logger.info(f'Created Bundle ID {bundle_id}')
        return bundle_id


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
