import pathlib

from codemagic import cli

from .argument_types import KeyAlias
from .argument_types import KeyPassword
from .argument_types import KeystorePassword


class KeystoreArgument(cli.Argument):
    KEYSTORE_PATH = cli.ArgumentProperties(
        key='keystore_path',
        type=pathlib.Path,
        description='Keystore path',
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        key='keystore_password',
        type=KeystorePassword,
        description='...',  # TODO
    )
    KEY_ALIAS = cli.ArgumentProperties(
        key='key_alias',
        type=KeyAlias,
        description='...',  # TODO
    )
    KEY_PASSWORD = cli.ArgumentProperties(
        key='key_password',
        type=KeyPassword,
        description='...',  # TODO
    )


class CreateKeyStoreArgument(cli.Argument):
    ...
