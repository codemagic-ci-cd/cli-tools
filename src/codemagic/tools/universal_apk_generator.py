#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo


class UniversalApkGeneratorError(cli.CliAppException):
    pass


class UniversalApkGeneratorArgument(cli.Argument):
    PATTERN = cli.ArgumentProperties(
        flags=('--pattern',),
        key='pattern',
        type=pathlib.Path,
        description='glob pattern to parse files, relative to current folder',
        argparse_kwargs={'required': False, 'default': '**/*.aab'},
    )

    KEYSTORE_PATH = cli.ArgumentProperties(
        flags=('--ks',),
        key='keystore_path',
        type=pathlib.Path,
        description='path to the keystore to sign the apk files with',
        argparse_kwargs={'required': False, 'default': None},
    )

    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        flags=('--ks-pass',),
        key='keystore_password',
        description='keystore password',
        argparse_kwargs={'required': False, 'default': None},
    )

    KEY_ALIAS = cli.ArgumentProperties(
        flags=('--ks-key-alias',),
        key='key_alias',
        description='keystore key alias',
        argparse_kwargs={'required': False, 'default': None},
    )

    KEY_PASSWORD = cli.ArgumentProperties(
        flags=('--key-pass',),
        key='key_password',
        description='keystore key password',
        argparse_kwargs={'required': False, 'default': None},
    )


@cli.common_arguments(*UniversalApkGeneratorArgument)
class UniversalApkGenerator(cli.CliApp, PathFinderMixin):
    """
    DEPRECATED! Generate universal APK files from Android App Bundles
    """

    def __init__(self,
                 pattern: pathlib.Path,
                 android_signing_info: Optional[AndroidSigningInfo],
                 **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.android_signing_info = android_signing_info

    @classmethod
    def get_executable_name(cls) -> str:
        return 'universal-apk'

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> UniversalApkGenerator:
        keystore_arguments = (
            UniversalApkGeneratorArgument.KEYSTORE_PATH,
            UniversalApkGeneratorArgument.KEYSTORE_PASSWORD,
            UniversalApkGeneratorArgument.KEY_ALIAS,
            UniversalApkGeneratorArgument.KEY_PASSWORD,
        )
        signing_info_args = [argument.from_args(cli_args) for argument in keystore_arguments]
        if any(signing_info_args) and not all(signing_info_args):
            raise UniversalApkGeneratorArgument.KEYSTORE_PATH.raise_argument_error(
                'either all signing info arguments should be specified, or none of them should')

        pattern = cli_args.pattern.expanduser()
        signing_info = AndroidSigningInfo(*signing_info_args) if all(signing_info_args) else None
        return UniversalApkGenerator(
            pattern=pattern,
            android_signing_info=signing_info,
            **cls._parent_class_kwargs(cli_args)
        )

    @cli.action('generate')
    def generate(self) -> List[pathlib.Path]:
        """
        DEPRECATED! Generate universal APK files from Android App Bundles
        """
        from .bundletool import BundleTool
        from .bundletool import BundleToolTypes

        self._deprecation_notice()
        signing_info_kwargs = {}
        if self.android_signing_info:
            signing_info_kwargs = {
                'keystore_path': self.android_signing_info.store_path,
                'keystore_password': BundleToolTypes.KeystorePassword(self.android_signing_info.store_pass),
                'key_alias': BundleToolTypes.KeyAlias(self.android_signing_info.key_alias),
                'key_password': BundleToolTypes.KeyPassword(self.android_signing_info.key_pass),
            }
        return BundleTool().build_universal_apks(self.pattern, **signing_info_kwargs)

    def _deprecation_notice(self):
        from .bundletool import BundleTool

        current_action = self.generate.action_name
        new_action = BundleTool.build_universal_apks.action_name
        msg = (
            f'Warning! Action "{self.get_executable_name()} {current_action}" '
            f'is deprecated and will be removed in future releases.\n'
            f'Please use action "{BundleTool.__name__.lower()} {new_action}" instead.\n'
            f'See "{BundleTool.__name__.lower()} --help" for more information.'
        )
        self.echo(Colors.YELLOW(msg))


if __name__ == '__main__':
    UniversalApkGenerator.invoke_cli()
