#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from codemagic_cli_tools import cli
from codemagic_cli_tools.apple import AppStoreConnectApiError
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import BundleIdPlatform
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.cli.colors import Colors
from .base_provisioning import BaseProvisioning


class AutomaticProvisioningError(cli.CliAppException):
    pass


class BundleIdArgument(cli.TypedCliArgument[str]):
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


class PrivateKeyPathArgument(cli.TypedCliArgument[pathlib.Path]):
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
    BUNDLE_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='bundle_id_resource_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Bundle ID',
    )
    BUNDLE_ID_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_id_identifier',
        type=BundleIdArgument,
        description='Identifier of the Bundle ID',
    )
    BUNDLE_ID_NAME = cli.ArgumentProperties(
        key='bundle_id_name',
        flags=('--bundle-id-name',),
        description='Name of the Bundle ID. By default will be deduced from Bundle ID identifier.',
        argparse_kwargs={'required': False},
    )
    CREATE_RESOURCE = cli.ArgumentProperties(
        key='create_resource',
        flags=('--create',),
        type=bool,
        description='Whether to create the resource if it does not exist yet',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
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
    IGNORE_NOT_FOUND = cli.ArgumentProperties(
        key='ignore_not_found',
        flags=('--ignore-not-found',),
        type=bool,
        description='Do not raise exceptions if the specified resource does not exist.',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
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
    def from_cli_args(cls, cli_args: argparse.Namespace):
        key_identifier_argument = AutomaticProvisioningArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AutomaticProvisioningArgument.ISSUER_ID.from_args(cli_args)
        if issuer_id_argument is None:
            raise AutomaticProvisioningArgument.ISSUER_ID.raise_argument_error()
        if key_identifier_argument is None:
            raise AutomaticProvisioningArgument.KEY_IDENTIFIER.raise_argument_error()

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
            private_key = private_key_argument.value
        else:
            private_key = private_key_path_argument.value.read_text()

        return AutomaticProvisioning(
            issuer_id=issuer_id_argument.value,
            key_identifier=key_identifier_argument.value,
            private_key=private_key,
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            log_requests=cli_args.log_requests,
        )

    @classmethod
    def _get_argument_value(cls, argument: Union[Any, cli.TypedCliArgument]) -> Any:
        if isinstance(argument, cli.TypedCliArgument):
            return argument.value
        return argument

    @cli.action('create-bundle-id',
                AutomaticProvisioningArgument.BUNDLE_ID_IDENTIFIER,
                AutomaticProvisioningArgument.BUNDLE_ID_NAME,
                AutomaticProvisioningArgument.JSON_OUTPUT,
                AutomaticProvisioningArgument.PLATFORM)
    def create_bundle_id(self,
                         bundle_id_identifier: Union[str, BundleIdArgument],
                         bundle_id_name: Optional[str] = None,
                         json_output: bool = False,
                         platform: BundleIdPlatform = BundleIdPlatform.IOS) -> BundleId:
        """
        Create Bundle ID in Apple Developer portal for specifier identifier.
        """

        identifier = self._get_argument_value(bundle_id_identifier)
        if bundle_id_name is None:
            bundle_id_name = identifier.replace('.', ' ')
        self.logger.info(
            f'Creating new Bundle ID "{identifier}" with name "{bundle_id_name}" for platform {platform}')
        try:
            bundle_id = self.api_client.bundle_ids.register(identifier, bundle_id_name, platform)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))
        self.logger.info(f'Created Bundle ID {bundle_id.id}')
        bundle_id.print(json_output)
        return bundle_id

    @cli.action('list-bundle-ids',
                AutomaticProvisioningArgument.BUNDLE_ID_IDENTIFIER,
                AutomaticProvisioningArgument.BUNDLE_ID_NAME,
                AutomaticProvisioningArgument.JSON_OUTPUT,
                AutomaticProvisioningArgument.PLATFORM)
    def list_bundle_ids(self,
                        bundle_id_identifier: Union[str, BundleIdArgument],
                        bundle_id_name: Optional[str] = None,
                        json_output: bool = False,
                        platform: BundleIdPlatform = BundleIdPlatform.IOS,
                        print_resources: bool = True) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints.
        """

        identifier = self._get_argument_value(bundle_id_identifier)
        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=identifier, name=bundle_id_name, platform=platform)
        try:
            bundle_ids = self.api_client.bundle_ids.list(bundle_id_filter=bundle_id_filter)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.logger.info(f'Found {len(bundle_ids)} Bundle IDs matching {bundle_id_filter}')
        if not bundle_ids:
            raise AutomaticProvisioningError(
                f'Did not find any bundle ids matching specified filters: {bundle_id_filter}')
        if print_resources:
            BundleId.print_resources(bundle_ids, json_output)
        return bundle_ids

    @cli.action('find-bundle-id',
                AutomaticProvisioningArgument.BUNDLE_ID_IDENTIFIER,
                AutomaticProvisioningArgument.CREATE_RESOURCE,
                AutomaticProvisioningArgument.JSON_OUTPUT,
                AutomaticProvisioningArgument.PLATFORM)
    def find_bundle_id(self,
                       bundle_id_identifier: Union[str, BundleIdArgument],
                       create_resource: bool = False,
                       json_output: bool = False,
                       platform: BundleIdPlatform = BundleIdPlatform.IOS) -> BundleId:
        """
        Find one Bundle ID from Apple Developer portal for specifier identifier.
        """

        identifier = self._get_argument_value(bundle_id_identifier)
        try:
            bundle_ids = self.list_bundle_ids(
                bundle_id_identifier, json_output=json_output, platform=platform, print_resources=False)
        except AutomaticProvisioningError:
            if not create_resource:
                raise
            self.logger.info(f'Bundle ID for identifier {identifier} not found.')
            return self.create_bundle_id(bundle_id_identifier, json_output=json_output, platform=platform)

        bundle_id = bundle_ids[0]
        self.logger.info(f'Found Bundle ID {bundle_id.id}')
        bundle_id.print(json_output)
        return bundle_id

    @cli.action('delete-bundle-id',
                AutomaticProvisioningArgument.BUNDLE_ID_RESOURCE_ID,
                AutomaticProvisioningArgument.IGNORE_NOT_FOUND)
    def delete_bundle_id(self, bundle_id_resource_id: ResourceId, ignore_not_found: bool = False) -> None:
        """
        Delete specified Bundle ID from Apple Developer portal.
        """
        self.logger.info(f'Delete Bundle ID {bundle_id_resource_id}')
        try:
            self.api_client.bundle_ids.delete(bundle_id_resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found and api_error.status_code == 404:
                self.logger.info(f'Bundle ID {bundle_id_resource_id} does not exist, did not delete.')
                return
            raise AutomaticProvisioningError(str(api_error))
        else:
            self.logger.info(f'Successfully deleted Bundle ID {bundle_id_resource_id}')


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
