from typing import Optional

from codemagic import cli

from .argument_types import KeyAlias
from .argument_types import KeyPassword
from .argument_types import KeystorePassword
from .argument_types import KeystorePath


class AndroidKeystoreArgument(cli.Argument):
    KEYSTORE_PATH = cli.ArgumentProperties(
        key='keystore_path',
        flags=('-k', '--ks', '--keystore'),
        type=KeystorePath,
        description='Path where your keystore should be created or read from',
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        key='keystore_password',
        flags=('-p', '--ks-pass', '--keystore-pass'),
        type=KeystorePassword,
        description='Secure password for your keystore',
        argparse_kwargs={'required': True},
    )
    KEY_ALIAS = cli.ArgumentProperties(
        key='key_alias',
        flags=('-a', '--ks-key-alias', '--alias'),
        type=KeyAlias,
        description='An identifying name for your keystore key',
        argparse_kwargs={'required': True},
    )
    KEY_PASSWORD = cli.ArgumentProperties(
        key='key_password',
        flags=('-l', '--ks-key-pass', '--key-pass'),
        type=Optional[KeyPassword],
        description=(
            'Secure password for your keystore key. '
            'Keystore password will be used in case it is not given.'
        ),
        argparse_kwargs={'required': False, 'default': None},
    )


class CreateKeyStoreArgument(cli.Argument):
    ...
