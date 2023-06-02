from __future__ import annotations

import json
import pathlib
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import Certificate
from codemagic.models import CertificateAttributes
from codemagic.models import Keystore
from codemagic.shell_tools import Keytool

from .argument_types import KeyPassword
from .argument_types import KeystorePassword
from .arguments import AndroidKeystoreArgument
from .arguments import AndroidKeystoreIssuerArgument
from .arguments import CreateAndroidKeystoreArgument


class AndroidKeystoreError(cli.CliAppException):
    pass


class AndroidKeystore(cli.CliApp, PathFinderMixin):
    """
    Manage your Android app code signing keystores
    """

    @classmethod
    def _get_certificate_attributes(
        cls,
        issuer_common_name: Optional[str],
        issuer_organization: Optional[str],
        issuer_organization_unit: Optional[str],
        issuer_locality: Optional[str],
        issuer_state_or_province: Optional[str],
        issuer_country: Optional[str],
        issuer_distinguished_name: Optional[str],
    ) -> CertificateAttributes:
        if issuer_distinguished_name is None:
            certificate_attributes = CertificateAttributes(
                common_name=issuer_common_name,
                organizational_unit=issuer_organization_unit,
                organization=issuer_organization,
                locality=issuer_locality,
                state_or_province=issuer_state_or_province,
                country=issuer_country,
            )
            if not certificate_attributes.is_valid():
                raise AndroidKeystoreIssuerArgument.COMMON_NAME.raise_argument_error('Missing issuer information')
        else:
            try:
                certificate_attributes = CertificateAttributes.from_distinguished_name(issuer_distinguished_name)
            except ValueError:
                error = f'Invalid distinguished name "{issuer_distinguished_name}"'
                raise AndroidKeystoreIssuerArgument.DISTINGUISHED_NAME.raise_argument_error(error)
            if not certificate_attributes.is_valid():
                error = 'Missing issuer information'
                raise AndroidKeystoreIssuerArgument.DISTINGUISHED_NAME.raise_argument_error(error)

        return certificate_attributes

    @cli.action(
        'create',
        AndroidKeystoreArgument.KEYSTORE_PATH,
        AndroidKeystoreArgument.KEYSTORE_PASSWORD,
        AndroidKeystoreArgument.KEY_ALIAS,
        AndroidKeystoreArgument.KEY_PASSWORD,
        CreateAndroidKeystoreArgument.OVERWRITE_EXISTING,
        CreateAndroidKeystoreArgument.VALIDITY_DAYS,
        *AndroidKeystoreIssuerArgument.with_custom_argument_group(
            'set keystore issuer information. At least one is required',
            *AndroidKeystoreIssuerArgument,
        ),
    )
    def create(
        self,
        keystore_path: pathlib.Path,
        keystore_password: Union[str, KeystorePassword],
        key_alias: str,
        key_password: Optional[Union[str, KeyPassword]] = None,
        issuer_common_name: Optional[str] = None,
        issuer_organization: Optional[str] = None,
        issuer_organization_unit: Optional[str] = None,
        issuer_locality: Optional[str] = None,
        issuer_state_or_province: Optional[str] = None,
        issuer_country: Optional[str] = None,
        issuer_distinguished_name: Optional[str] = None,
        overwrite_existing: bool = False,
        validity_days: int = CreateAndroidKeystoreArgument.VALIDITY_DAYS.get_default(),
    ) -> Keystore:
        """
        Create an Android keystore
        """
        certificate_attributes = self._get_certificate_attributes(
            issuer_common_name,
            issuer_organization,
            issuer_organization_unit,
            issuer_locality,
            issuer_state_or_province,
            issuer_country,
            issuer_distinguished_name,
        )

        store_password: str = KeystorePassword.resolve_value(keystore_password)
        if key_password is None:
            _key_password: str = store_password
        else:
            _key_password = KeyPassword.resolve_value(key_password)

        keystore = Keystore(
            certificate_attributes=certificate_attributes,
            key_alias=key_alias,
            key_password=_key_password,
            store_path=keystore_path,
            store_password=store_password,
            validity=validity_days,
        )
        self.logger.info(Colors.GREEN(f'Create Android keystore at {keystore.store_path}'))
        if keystore.store_path.exists():
            if overwrite_existing:
                self.logger.info(f'Remove existing keystore from {keystore.store_path}')
                keystore.store_path.unlink()
            else:
                error = f'Keystore already exists at {keystore.store_path}'
                raise AndroidKeystoreArgument.KEYSTORE_PATH.raise_argument_error(error)

        keystore.store_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            Keytool().generate_keystore(keystore)
        except IOError:
            raise AndroidKeystoreError('Creating keystore failed')
        return keystore

    @cli.action(
        'create-debug-keystore',
        CreateAndroidKeystoreArgument.OVERWRITE_EXISTING,
        CreateAndroidKeystoreArgument.VALIDITY_DAYS,
    )
    def create_debug_keystore(
        self,
        overwrite_existing: bool = False,
        validity_days: int = CreateAndroidKeystoreArgument.VALIDITY_DAYS.get_default(),
    ) -> Keystore:
        """
        Create Android debug keystore at ~/.android/debug.keystore
        """
        return self.create(
            keystore_path=pathlib.Path('~/.android/debug.keystore').expanduser(),
            key_alias='androiddebugkey',
            keystore_password='android',
            issuer_common_name='Android Debug',
            issuer_organization='Android',
            issuer_country='US',
            overwrite_existing=overwrite_existing,
            validity_days=validity_days,
        )

    @cli.action(
        'verify',
        AndroidKeystoreArgument.KEYSTORE_PATH,
        AndroidKeystoreArgument.KEYSTORE_PASSWORD,
        AndroidKeystoreArgument.KEY_ALIAS,
    )
    def verify(
        self,
        keystore_path: pathlib.Path,
        keystore_password: Union[str, KeystorePassword],
        key_alias: str,
    ):
        """
        Check that the keystore password, key password and key alias are correct
        for specified keystore
        """
        store_password: str = KeystorePassword.resolve_value(keystore_password)

        self.logger.info(f'Verify Android keystore at "{keystore_path}"')
        self._assert_keystore_exists(keystore_path)

        try:
            Keytool().validate_keystore(
                keystore_path=keystore_path,
                keystore_password=store_password,
                key_alias=key_alias,
            )
        except ValueError as ve:
            raise AndroidKeystoreError(str(ve)) from ve
        self.logger.info((
            f'Keystore "{keystore_path}" has alias "{key_alias}" '
            f'and can be unlocked with given password'
        ))

    @cli.action(
        'certificate',
        AndroidKeystoreArgument.KEYSTORE_PATH,
        AndroidKeystoreArgument.KEYSTORE_PASSWORD,
        AndroidKeystoreArgument.KEY_ALIAS,
        AndroidKeystoreArgument.JSON_OUTPUT,
    )
    def get_certificate(
        self,
        keystore_path: pathlib.Path,
        keystore_password: Union[str, KeystorePassword],
        key_alias: str,
        json_output: bool = False,
        should_print: bool = True,
    ) -> Certificate:
        """
        Extract certificate for specified alias from the keystore
        """
        store_password: str = KeystorePassword.resolve_value(keystore_password)

        self.logger.info(f'Get certificate in Android keystore "{keystore_path}" for alias "{key_alias}"')
        self._assert_keystore_exists(keystore_path)

        try:
            certificate = Keytool().get_certificate(
                keystore_path=keystore_path,
                keystore_password=store_password,
                key_alias=key_alias,
            )
        except ValueError as ve:
            raise AndroidKeystoreError(str(ve)) from ve

        if should_print:
            if json_output:
                summary = json.dumps(certificate.get_summary(), indent=4)
            else:
                summary = certificate.get_text_summary()
            self.echo(summary)

        return certificate

    @cli.action(
        'certificates',
        AndroidKeystoreArgument.KEYSTORE_PATH,
        AndroidKeystoreArgument.KEYSTORE_PASSWORD,
        AndroidKeystoreArgument.KEY_ALIAS_OPTIONAL,
        AndroidKeystoreArgument.JSON_OUTPUT,
    )
    def list_certificates(
        self,
        keystore_path: pathlib.Path,
        keystore_password: Union[str, KeystorePassword],
        key_alias: Optional[str] = None,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Certificate]:
        """
        List certificates that are included in keystore
        """
        store_password: str = KeystorePassword.resolve_value(keystore_password)

        if key_alias is None:
            self.logger.info(f'List certificates in Android keystore "{keystore_path}"')
        else:
            self.logger.info(f'List certificates in Android keystore "{keystore_path}" for alias "{key_alias}"')

        self._assert_keystore_exists(keystore_path)

        try:
            certificates = Keytool().get_certificates(
                keystore_path=keystore_path,
                keystore_password=store_password,
                key_alias=key_alias,
            )
        except ValueError as ve:
            raise AndroidKeystoreError(str(ve)) from ve

        if should_print:
            if json_output:
                summary = json.dumps([c.get_summary() for c in certificates], indent=4)
            else:
                summary = '\n'.join([c.get_text_summary() for c in certificates])
            self.echo(summary)

        return certificates

    @classmethod
    def _assert_keystore_exists(cls, keystore_path: pathlib.Path):
        if not keystore_path.is_file():
            error = f'Keystore does not exists at {keystore_path}'
            raise AndroidKeystoreArgument.KEYSTORE_PATH.raise_argument_error(error)


if __name__ == '__main__':
    AndroidKeystore.invoke_cli()
