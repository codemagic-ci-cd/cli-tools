from __future__ import annotations

import argparse
import pathlib

from codemagic import cli
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo

from .arguments import AndroidKeystoreArgument


@cli.common_arguments(*AndroidKeystoreArgument)
class AndroidKeystore(cli.CliApp, PathFinderMixin):
    """
    Manage your Android app code signing Keystores
    """

    def __init__(
            self,
            keystore_path: pathlib.Path,
            keystore_password: str,
            key_alias: str,
            key_password: str,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._path = keystore_path
        self._keystore_password = keystore_password
        self._key_alias = key_alias
        self._key_password = key_password

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> AndroidKeystore:
        keystore_path = AndroidKeystoreArgument.KEYSTORE_PATH.from_args(cli_args)
        keystore_password = AndroidKeystoreArgument.KEYSTORE_PASSWORD.from_args(cli_args)
        key_alias = AndroidKeystoreArgument.KEY_ALIAS.from_args(cli_args)
        key_password = AndroidKeystoreArgument.KEY_PASSWORD.from_args(cli_args)
        return cls(
            keystore_path=keystore_path,
            keystore_password=keystore_password,
            key_alias=key_alias,
            key_password=key_password or keystore_password,
        )

    @cli.action('create')
    def create(self) -> AndroidSigningInfo:
        """
        Create an Android keystore
        """
        return AndroidSigningInfo(
            store_path=self._path,
            store_pass=self._keystore_password,
            key_alias=self._key_alias,
            key_pass=self._key_password,
        )


if __name__ == '__main__':
    AndroidKeystore.invoke_cli()
