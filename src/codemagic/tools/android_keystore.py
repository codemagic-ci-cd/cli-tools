import pathlib

from codemagic import cli
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo

from ._android_keystore.argument_types import KeyAlias
from ._android_keystore.argument_types import Password
from ._android_keystore.arguments import KeystoreArgument


@cli.common_arguments(KeystoreArgument.KEYSTORE_PATH)
class AndroidKeystore(cli.CliApp, PathFinderMixin):
    """
    Manage your Android app code signing Keystores
    """

    def __init__(self, keystore_path: pathlib.Path, **kwargs):
        super().__init__(**kwargs)
        self._path = keystore_path

    @cli.action('create')
    def create(
            self,
            keystore_password: Password,
            key_password: Password,
            key_alias: KeyAlias,
    ) -> AndroidSigningInfo:
        """
        Create an Android keystore
        """
        raise NotImplementedError()


if __name__ == '__main__':
    AndroidKeystore.invoke_cli()
