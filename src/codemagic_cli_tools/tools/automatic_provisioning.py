#!/usr/bin/env python3

from __future__ import annotations

import pathlib

from codemagic_cli_tools import cli
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from .base_provisioning import BaseProvisioning


class AutomaticProvisioningError(cli.CliAppException):
    pass


class AutomaticProvisioningArgument(cli.Argument):
    ISSUER_ID = cli.ArgumentProperties(
        key='issuer_id',
        flags=('--issuer-id',),
        type=IssuerId,
        description='App Store Connect API Key Issuer ID. '
                    'Identifies the issuer who created the authentication token. '
                    f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        argparse_kwargs={'required': True},
    )
    KEY_IDENTIFIER = cli.ArgumentProperties(
        key='key_identifier',
        flags=('--key-id',),
        type=KeyIdentifier,
        description='App Store Connect API Key ID. '
                    f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        argparse_kwargs={'required': True},
    )
    PRIVATE_KEY_PATH = cli.ArgumentProperties(
        key='private_key_path',
        flags=('--private-key-path',),
        type=pathlib.Path,
        description='Path to the App Store Connect API private key. '
                    f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.',
        argparse_kwargs={'required': True},
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
    AutomaticProvisioningArgument.PRIVATE_KEY_PATH,
)
class AutomaticProvisioning(BaseProvisioning):
    """
    Utility to download code signing certificates and provisioning profiles
    from Apple Developer Portal using App Store Connect API to perform iOS code signing.
    """

    def __init__(self, key_identifier: KeyIdentifier, issuer_id: IssuerId, private_key_path: pathlib.Path, **kwargs):
        super().__init__(**kwargs)
        self.api_client = AppStoreConnectApiClient(
            key_identifier,
            issuer_id,
            private_key_path.expanduser().read_text())

    @cli.action('fetch', AutomaticProvisioningArgument.BUNDLE_IDENTIFIER)
    def fetch(self, bundle_identifier: str):
        """
        Fetch code signing files from Apple Developer portal for
        specified bundle identifier
        """
        # TODO Apple Developer Portal communication
        self.api_client.bundle_ids.list()


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
