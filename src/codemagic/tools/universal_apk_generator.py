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
    Generate universal APK files from Android App Bundles.
    DEPRECATED! Use `android-app-bundle` instead
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
            **cls._parent_class_kwargs(cli_args),
        )

    @cli.action('generate')
    def generate(self) -> List[pathlib.Path]:
        """
        Generate universal APK files from Android App Bundles.
        DEPRECATED! Use `android-app-bundle build-universal-apk` instead
        """
        from .android_app_bundle import AndroidAppBundle
        from .android_app_bundle import AndroidAppBundleTypes

        self._deprecation_notice()
        android_app_bundle = AndroidAppBundle()
        if self.android_signing_info:
            apk_paths = android_app_bundle.build_universal_apks(
                self.pattern,
                keystore_path=self.android_signing_info.store_path,
                keystore_password=AndroidAppBundleTypes.KeystorePassword(self.android_signing_info.store_pass),
                key_alias=AndroidAppBundleTypes.KeyAlias(self.android_signing_info.key_alias),
                key_password=AndroidAppBundleTypes.KeyPassword(self.android_signing_info.key_pass),
            )
        else:
            apk_paths = android_app_bundle.build_universal_apks(self.pattern)
        return apk_paths

    def _deprecation_notice(self):
        from .android_app_bundle import AndroidAppBundle

        current_action = f'{self.get_executable_name()} {self.generate.action_name}'
        new_action = f'{AndroidAppBundle.get_executable_name()} {AndroidAppBundle.build_universal_apks.action_name}'
        lines = (
            f'Warning! Action "{current_action}" is deprecated and will be removed in future releases.',
            f'Please use action "{new_action}" instead.',
            f'See "{AndroidAppBundle.get_executable_name()} --help" for more information.',
        )
        for line in lines:
            self.logger.info(Colors.YELLOW(line))


if __name__ == '__main__':
    UniversalApkGenerator.invoke_cli()
