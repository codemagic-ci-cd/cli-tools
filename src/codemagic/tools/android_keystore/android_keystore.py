from __future__ import annotations

import pathlib
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import CertificateAttributes
from codemagic.models import Keystore
from codemagic.shell_tools import Keytool

from .argument_types import CommonName
from .argument_types import Country
from .argument_types import DistinguishedName
from .argument_types import KeyAlias
from .argument_types import KeyPassword
from .argument_types import KeystorePassword
from .argument_types import KeystorePath
from .argument_types import Locality
from .argument_types import Organization
from .argument_types import OrganizationUnit
from .argument_types import StateOrProvince
from .arguments import AndroidKeystoreArgument
from .arguments import AndroidKeystoreIssuerArgument
from .arguments import CreateAndroidKeystoreArgument


class AndroidKeystoreError(cli.CliAppException):
    pass


class AndroidKeystore(cli.CliApp, PathFinderMixin):
    """
    Manage your Android app code signing Keystores
    """

    @classmethod
    def _get_certificate_attributes(
            cls,
            issuer_common_name: Optional[Union[str, CommonName]],
            issuer_organization: Optional[Union[str, Organization]],
            issuer_organization_unit: Optional[Union[str, OrganizationUnit]],
            issuer_locality: Optional[Union[str, Locality]],
            issuer_state_or_province: Optional[Union[str, StateOrProvince]],
            issuer_country: Optional[Union[str, Country]],
            issuer_distinguished_name: Optional[Union[str, DistinguishedName]],
    ) -> CertificateAttributes:
        if issuer_distinguished_name is None:
            certificate_attributes = CertificateAttributes(
                common_name=CommonName.resolve_optional_value(issuer_common_name),
                organizational_unit=OrganizationUnit.resolve_optional_value(issuer_organization_unit),
                organization=Organization.resolve_optional_value(issuer_organization),
                locality=Locality.resolve_optional_value(issuer_locality),
                state_or_province=StateOrProvince.resolve_optional_value(issuer_state_or_province),
                country=Country.resolve_optional_value(issuer_country),
            )
            if not certificate_attributes.is_valid():
                raise AndroidKeystoreIssuerArgument.COMMON_NAME.raise_argument_error('Missing issuer information')
        else:
            distinguished_name = DistinguishedName.resolve_value(issuer_distinguished_name)
            try:
                certificate_attributes = CertificateAttributes.from_distinguished_name(distinguished_name)
            except ValueError:
                error = f'Invalid distinguished name "{distinguished_name}"'
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
        *AndroidKeystoreIssuerArgument.with_custom_argument_group(
            'set keystore issuer information. At least one is required',
            *AndroidKeystoreIssuerArgument,
        ),
    )
    def create(
            self,
            keystore_path: Union[pathlib.Path, KeystorePath],
            keystore_password: Union[str, KeystorePassword],
            key_alias: Union[str, KeyAlias],
            key_password: Optional[Union[str, KeyPassword]] = None,
            issuer_common_name: Optional[Union[str, CommonName]] = None,
            issuer_organization: Optional[Union[str, Organization]] = None,
            issuer_organization_unit: Optional[Union[str, OrganizationUnit]] = None,
            issuer_locality: Optional[Union[str, Locality]] = None,
            issuer_state_or_province: Optional[Union[str, StateOrProvince]] = None,
            issuer_country: Optional[Union[str, Country]] = None,
            issuer_distinguished_name: Optional[Union[str, DistinguishedName]] = None,
            overwrite_existing: bool = False,
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
            key_alias=KeyAlias.resolve_value(key_alias),
            key_password=_key_password,
            store_path=KeystorePath.resolve_value(keystore_path),
            store_password=store_password,
        )
        self.logger.info(Colors.GREEN(f'Create Android debug keystore at {keystore.store_path}'))
        if keystore.store_path.exists():
            if overwrite_existing:
                self.logger.info(f'Remove existing keystore from {keystore.store_path}')
                keystore.store_path.unlink()
            else:
                raise AndroidKeystoreError(f'Keystore already exists at {keystore.store_path}')

        keystore.store_path.parent.mkdir(parents=True, exist_ok=True)
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
