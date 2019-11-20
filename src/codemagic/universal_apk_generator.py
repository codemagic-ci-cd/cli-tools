#!/usr/bin/env python3

import argparse
import collections
import pathlib
import tempfile
import urllib.request
import zipfile
from typing import NoReturn, Optional

from . import cli, models


class Keystore(cli.EnvironmentArgumentValue):
    pass


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

    BUNDLETOOL_PATH = cli.ArgumentProperties(
        flags=('--pattern',),
        key='bundletool_path',
        type=pathlib.Path,
        description='glob pattern to parse files, relative to current folder',
        argparse_kwargs={'required': False, 'default': models.Bundletool.DEFAULT_PATH},
    )

    KEYSTORE = cli.ArgumentProperties(
        flags=('--ks',),
        key='keystore',
        type=Keystore,
        description='keystore to sign the apk files with',
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
        key='key_lias',
        description='keystore key alias',
        argparse_kwargs={'required': False, 'default': None},
    )

    KEY_PASSWORD = cli.ArgumentProperties(
        flags=('--key-pass',),
        key='key_password',
        description='keystore key password',
        argparse_kwargs={'required': False, 'default': None},
    )


SigningInfo = collections.namedtuple('SigningInfo', 'store_path store_pass key_alias key_pass')


class UniversalApkGenerator(cli.CliApp):
    """
    Generate universal APK files from Android App Bundles
    """

    def __init__(self, bundletool_path: pathlib.Path, pattern: pathlib.Path, signing_info: Optional[SigningInfo] = None):
        super().__init__()
        self.bundletool_path = bundletool_path
        self.pattern = pattern
        self.signing_info = signing_info

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        keystore_arguments = (
            UniversalApkGeneratorArgument.KEYSTORE,
            UniversalApkGeneratorArgument.KEYSTORE_PASSWORD,
            UniversalApkGeneratorArgument.KEY_ALIAS,
            UniversalApkGeneratorArgument.KEY_PASSWORD,
        )
        signing_info_args = (getattr(cli_args, a.value.key) for a in keystore_arguments)

        if any(signing_info_args) and not all(signing_info_args):
            raise UniversalApkGeneratorError(
                'either all signing info arguments should be specified, or none of them should')

        pattern = cli_args.pattern.expanduser()
        if pattern.is_absolute():
            pattern = pattern.relative_to(pattern.anchor)

        return UniversalApkGenerator(
            bundletool_path=cli_args.bundletool,
            pattern=pattern,
            signing_info=SigningInfo(*signing_info_args) if signing_info_args else None,
        )

    @cli.action('generate', UniversalApkGeneratorArgument.KEYSTORE, UniversalApkGeneratorArgument.KEYSTORE_PASSWORD, UniversalApkGeneratorArgument.KEY_ALIAS, UniversalApkGeneratorArgument.KEY_PASSWORD)
    def generate(self) -> NoReturn:
        """
        Generate universal APK files from Android App Bundles
        """
        self.logger.info(f'Searching for files in {self.pattern.resolve()}')
        with tempfile.TemporaryDirectory() as d:
            if not self.bundletool_path.exists():
                self.bundletool_path = pathlib.Path(d) / 'bundletool.jar'
                self.logger.info(f'Downloading bundletool to {self.bundletool_path}')
                urllib.request.urlretrieve(models.Bundletool.DOWNLOAD_URL, self.bundletool_path)

            did_find_paths = False
            for path in pathlib.Path().glob(str(self.pattern)):
                did_find_paths = True
                self.logger.info(f'Generating universal apk for {path}')
                apk_path = self._generate_apk(path)
                self.logger.info(f'Generated {apk_path.resolve()}')

        if not did_find_paths:
            raise UniversalApkGeneratorError('Did not find any matching files to generate apk from')

    def _generate_apk(self, path):
        apk_path = self._get_apk_path(path)

        with tempfile.TemporaryDirectory() as d:
            apks_path = pathlib.Path(d) / 'universal.apks'

            command = [
                'java', '-jar', str(self.bundletool_path),
                'build-apks', '--mode', 'universal',
                '--bundle', str(path), '--output', str(apks_path)
            ]
            obfuscate_patterns = []

            if self.signing_info:
                command.extend([
                    '--ks', self.signing_info.store_path, '--ks-pass', f'pass:{self.signing_info.store_pass}',
                    '--ks-key-alias', self.signing_info.key_alias, '--key-pass', f'pass:{self.signing_info.key_pass}',
                ])
                obfuscate_patterns = [self.signing_info.store_pass, self.signing_info.key_pass]

            process = self.execute(command, obfuscate_patterns=obfuscate_patterns)
            if process.returncode != 0:
                raise UniversalApkGeneratorError(f'Unable to generate apks file for bundle {path}', process)
            self.logger.info('Extracting universal apk')
            with zipfile.ZipFile(apks_path, 'r') as zf, open(apk_path, 'wb+') as of:
                of.write(zf.read('universal.apk'))
        return apk_path

    @staticmethod
    def _get_apk_path(aab_path):
        return aab_path.parent / f'{aab_path.stem}-universal.apk'


if __name__ == '__main__':
    UniversalApkGenerator.invoke_cli()
