import argparse

from codemagic import cli


class Password(cli.EnvironmentArgumentValue[str]):
    @classmethod
    def _apply_type(cls, non_typed_value: str) -> str:
        value = super()._apply_type(non_typed_value)
        if len(value) < 6:
            raise argparse.ArgumentTypeError('Minimum required password length is 6 characters')
        return value


class KeystorePassword(Password):
    environment_variable_key = 'ANDROID_KEYSTORE_PASSWORD'


class KeyPassword(Password):
    environment_variable_key = 'ANDROID_KEYSTORE_KEY_PASSWORD'


def two_letter_country_code(country: str) -> str:
    if len(country) != 2:
        raise argparse.ArgumentTypeError('Two-letter country code is required')
    return country
