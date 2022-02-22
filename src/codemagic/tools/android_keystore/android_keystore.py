from __future__ import annotations

import pathlib
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import CertificateAttributes
from codemagic.models import Keystore
from codemagic.shell_tools import Keytool

from .arguments import CreateAndroidKeystoreArgument


class AndroidKeystoreError(cli.CliAppException):
    pass


class AndroidKeystore(cli.CliApp, PathFinderMixin):
    """
    Manage your Android app code signing Keystores
    """

    @cli.action(
        'create',
        CreateAndroidKeystoreArgument.OVERWRITE_EXISTING,
    )
    def create(
            self,
            keystore_path: pathlib.Path,
            key_alias: str,
            store_password: str,
            issuer_common_name: Optional[str] = None,
            issuer_organization: Optional[str] = None,
            issuer_organization_unit: Optional[str] = None,
            issuer_locality: Optional[str] = None,
            issuer_state_or_province: Optional[str] = None,
            issuer_country: Optional[str] = None,
            overwrite_existing: bool = False,
    ) -> Keystore:
        """
        Create an Android keystore
        """
        certificate_attributes = CertificateAttributes(
            common_name=issuer_common_name,
            organizational_unit=issuer_organization_unit,
            organization=issuer_organization,
            locality=issuer_locality,
            state_or_province=issuer_state_or_province,
            country=issuer_country,
        )
        if not certificate_attributes.is_valid():
            # TODO: Raise error from CLI argument
            raise AndroidKeystoreError('Some issuer information is required to generate keystore')

        keystore = Keystore(
            certificate_attributes=certificate_attributes,
            key_alias=key_alias,
            path=keystore_path,
            store_password=store_password,
        )
        self.logger.info(Colors.GREEN(f'Create Android debug keystore at {keystore_path}'))
        if keystore.path.exists():
            if overwrite_existing:
                self.logger.info(f'Remove existing keystore from {keystore_path}')
                keystore.path.unlink()
            else:
                raise AndroidKeystoreError(f'Keystore already exists at {keystore.path}')

        keystore_path.parent.mkdir(parents=True, exist_ok=True)
        Keytool().generate_keystore(keystore)
        return keystore

    @cli.action(
        'create-debug-keystore',
        CreateAndroidKeystoreArgument.OVERWRITE_EXISTING,
    )
    def create_debug_keystore(
            self,
            overwrite_existing: bool = False,
    ) -> Keystore:
        """
        Create Android debug keystore at ~/.android/debug.keystore
        """
        return self.create(
            keystore_path=pathlib.Path('~/.android/debug.keystore').expanduser(),
            key_alias='androiddebugkey',
            store_password='android',
            issuer_common_name='Android Debug',
            issuer_organization='Android',
            issuer_country='US',
            overwrite_existing=overwrite_existing,
        )


if __name__ == '__main__':
    AndroidKeystore.invoke_cli()
