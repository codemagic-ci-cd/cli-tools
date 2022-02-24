import argparse
import pathlib

from codemagic import cli


class Password(cli.EnvironmentArgumentValue[str]):
    @classmethod
    def _apply_type(cls, non_typed_value: str) -> str:
        value = super()._apply_type(non_typed_value)
        if len(value) < 6:
            raise argparse.ArgumentTypeError('Minimum required password length is 6 characters')
        return value


class KeystorePath(cli.EnvironmentArgumentValue[pathlib.Path]):
    argument_type = pathlib.Path
    environment_variable_key = 'ANDROID_KEYSTORE_PATH'


class KeystorePassword(Password):
    environment_variable_key = 'ANDROID_KEYSTORE_PASSWORD'


class KeyAlias(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_KEY_ALIAS'


class KeyPassword(Password):
    environment_variable_key = 'ANDROID_KEYSTORE_KEY_PASSWORD'


class DistinguishedName(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_DISTINGUISHED_NAME'


class CommonName(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_COMMON_NAME'


class Organization(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_ORGANIZATION'


class OrganizationUnit(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_ORGANIZATION_UNIT'


class Locality(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_LOCALITY'


class StateOrProvince(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_STATE_OR_PROVINCE'


class Country(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_ISSUER_COUNTRY'

    @classmethod
    def _apply_type(cls, non_typed_value: str) -> str:
        value = super()._apply_type(non_typed_value)
        if len(value) != 2:
            raise argparse.ArgumentTypeError('Two-letter country code is required')
        return value
