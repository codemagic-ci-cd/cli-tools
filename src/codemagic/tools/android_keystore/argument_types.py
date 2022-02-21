import pathlib

from codemagic import cli


class KeystorePath(cli.EnvironmentArgumentValue[pathlib.Path]):
    argument_type = pathlib.Path
    environment_variable_key = 'ANDROID_KEYSTORE_PATH'


class KeystorePassword(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_PASSWORD'


class KeyPassword(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_KEY_PASSWORD'


class KeyAlias(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'ANDROID_KEYSTORE_KEY_ALIAS'
