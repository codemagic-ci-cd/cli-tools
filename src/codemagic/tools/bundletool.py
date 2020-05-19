import pathlib
import zipfile
from functools import lru_cache
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo


class BundleToolTypes:
    class KeyAlias(str):
        pass

    class _Password(cli.EnvironmentArgumentValue[str]):
        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return bool(value)

    class KeystorePassword(_Password):
        environment_variable_key = 'KEYSTORE_PASSWORD'

    class KeyPassword(_Password):
        environment_variable_key = 'KEYSTORE_KEY_PASSWORD'


class BundleToolError(cli.CliAppException):
    pass


class BundleToolArgument(cli.Argument):
    BUNDLE_PATTERN = cli.ArgumentProperties(
        flags=('--bundle',),
        key='aab_pattern',
        type=pathlib.Path,
        description='Glob pattern to parse files, relative to current folder',
        argparse_kwargs={
            'default': '**/*.aab',
            'required': False,
        },
    )
    KEYSTORE_PATH = cli.ArgumentProperties(
        flags=('--ks',),
        key='keystore_path',
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to the keystore to sign the apk files with',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        flags=('--ks-pass',),
        key='keystore_password',
        type=BundleToolTypes.KeystorePassword,
        description='Keystore password',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEY_ALIAS = cli.ArgumentProperties(
        flags=('--ks-key-alias',),
        key='key_alias',
        type=BundleToolTypes.KeyAlias,
        description='Keystore key alias',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEY_PASSWORD = cli.ArgumentProperties(
        flags=('--key-pass',),
        key='key_password',
        type=BundleToolTypes.KeyPassword,
        description='Keystore key password',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    BUILD_APKS_MODE = cli.ArgumentProperties(
        flags=('--mode',),
        key='mode',
        description=(
            'Set the mode to universal if you want bundletool to build only a single APK '
            'that includes all of your app\'s code and resources such that the APK is '
            'compatible with all device configurations your app supports.'
        ),
        argparse_kwargs={
            'default': None,
            'required': False,
            'choices': ['universal'],
        }
    )


@cli.common_arguments()
class BundleTool(cli.CliApp, PathFinderMixin):
    """
    Manage Android App Bundles using Bundletool
    """

    @property
    @lru_cache(1)
    def _jar_path(self) -> pathlib.Path:
        current_dir = pathlib.Path(__file__).parent.resolve()
        binaries_dir = current_dir.parent.parent.parent / 'bin'
        bundletool_jar = next(binaries_dir.glob('bundletool*.jar'), None)
        if not bundletool_jar:
            raise IOError(f'BundleTool jar not available in {current_dir}')
        return bundletool_jar.resolve()

    @classmethod
    def _get_android_signing_info(
            cls,
            keystore_path: Optional[pathlib.Path] = None,
            keystore_password: Optional[BundleToolTypes.KeystorePassword] = None,
            key_alias: Optional[BundleToolTypes.KeyAlias] = None,
            key_password: Optional[BundleToolTypes.KeyPassword] = None) -> Optional[AndroidSigningInfo]:
        signing_info = AndroidSigningInfo(
            store_path=keystore_path,
            store_pass=keystore_password.value if key_password else '',
            key_alias=key_alias,
            key_pass=key_password.value if key_password else '')

        if any(signing_info) and not all(signing_info):
            raise BundleToolArgument.KEYSTORE_PATH.raise_argument_error(
                'Either all signing info arguments should be specified, or none of them should')

        return signing_info if all(signing_info) else None

    @cli.action('version')
    def version(self) -> str:
        """ Get BundleTool version """
        self.logger.info(f'Get Bundletool version')
        process = self.execute(('java', '-jar', str(self._jar_path), 'version'), show_output=False)
        if process.returncode != 0:
            raise BundleToolError('Unable to get Bundletool version', process)
        version = process.stdout.strip()
        self.echo(version)
        return version

    @cli.action('build-apks',
                BundleToolArgument.BUNDLE_PATTERN,
                BundleToolArgument.KEYSTORE_PATH,
                BundleToolArgument.KEYSTORE_PASSWORD,
                BundleToolArgument.KEY_ALIAS,
                BundleToolArgument.KEY_PASSWORD,
                BundleToolArgument.BUILD_APKS_MODE)
    def build_apks(
            self,
            aab_pattern: pathlib.Path,
            keystore_path: Optional[pathlib.Path] = None,
            keystore_password: Optional[BundleToolTypes.KeystorePassword] = None,
            key_alias: Optional[BundleToolTypes.KeyAlias] = None,
            key_password: Optional[BundleToolTypes.KeyPassword] = None,
            mode: Optional[str] = None,
            should_print: bool = True) -> List[pathlib.Path]:
        """
        Generates an APK Set archive containing either all possible split APKs and
        standalone APKs or APKs optimized for the connected device (see connected-
        device flag). Returns list of generated APK set archives.
        """
        signing_info = self._get_android_signing_info(keystore_path, keystore_password, key_alias, key_password)

        aab_paths = [
            aab_path for aab_path in self.find_paths(aab_pattern.expanduser())
            if 'intermediates' not in aab_path.parts  # Exclude intermediate Android app bundles
        ]
        if aab_paths:
            self.logger.info(f'Found {len(aab_paths)} matching files')
        else:
            raise BundleToolError('Did not find any matching Android app bundles from which to generate APKs')

        apks_paths = []
        for aab_path in aab_paths:
            apks_path = self._build_apk_set_archive(aab_path, signing_info=signing_info, mode=mode)
            apks_paths.append(apks_path)
            if should_print:
                self.echo(str(apks_path))
        return apks_paths

    @cli.action('build-universal-apk',
                BundleToolArgument.BUNDLE_PATTERN,
                BundleToolArgument.KEYSTORE_PATH,
                BundleToolArgument.KEYSTORE_PASSWORD,
                BundleToolArgument.KEY_ALIAS,
                BundleToolArgument.KEY_PASSWORD)
    def build_universal_apks(
            self,
            aab_pattern: pathlib.Path,
            keystore_path: Optional[pathlib.Path] = None,
            keystore_password: Optional[BundleToolTypes.KeystorePassword] = None,
            key_alias: Optional[BundleToolTypes.KeyAlias] = None,
            key_password: Optional[BundleToolTypes.KeyPassword] = None) -> List[pathlib.Path]:
        """
        Shortcut for 'build-apks' action to build universal APKs from bundles.
        """

        apks_paths = self.build_apks(
            aab_pattern,
            keystore_path=keystore_path,
            keystore_password=keystore_password,
            key_alias=key_alias,
            key_password=key_password,
            mode='universal',
            should_print=False,
        )

        apk_paths = []
        for apks_path in apks_paths:
            apk_path = self._extract_universal_apk(apks_path)
            apk_paths.append(apk_path)
            self.echo(str(apk_path))
            apks_path.unlink()

        return apk_paths

    @cli.action('validate')
    def validate(self):
        """
        Verify that given Android App Bundle is valid and print
        out information about it.
        """

    @cli.action('dump')
    def dump(self):
        """
        Get files list or extract values from the bundle in a human-readable form.
        """

    @cli.action('get-size')
    def get_size(self):
        """
        Get the min and max download sizes of APKs served to different devices
        configurations from an APK Set.
        """

    def _build_apk_set_archive(self,
                               aab_path: pathlib.Path,
                               *,
                               signing_info: Optional[AndroidSigningInfo],
                               mode: Optional[str] = None) -> pathlib.Path:
        self.logger.info(f'Generating APKs from bundle {aab_path}')
        apks_path = aab_path.parent / f'{aab_path.stem}.apks'
        command = [
            'java', '-jar', str(self._jar_path), 'build-apks',
            '--bundle', str(aab_path),
            '--output', str(apks_path),
            *(['--mode', mode] if mode else []),
        ]
        if signing_info:
            store_pass_arg = f'pass:{signing_info.store_pass}'
            key_pass_arg = f'pass:{signing_info.key_pass}'
            command.extend([
                '--ks', signing_info.store_path,
                '--ks-pass', store_pass_arg,
                '--ks-key-alias', signing_info.key_alias,
                '--key-pass', key_pass_arg,
            ])
            obfuscate_patterns = [key_pass_arg, store_pass_arg]
        else:
            obfuscate_patterns = []

        process = self.execute(command, obfuscate_patterns=obfuscate_patterns)
        if process.returncode != 0:
            raise BundleToolError(f'Unable to generate apks file for bundle {aab_path}', process)
        self.logger.info(f'Generated {apks_path}')
        return apks_path

    def _extract_universal_apk(self, apks_path: pathlib.Path) -> pathlib.Path:
        self.logger.info(f'Extracting universal APK from {apks_path}')
        apk_path = apks_path.parent / f'{apks_path.stem}-universal.apk'
        with zipfile.ZipFile(apks_path, 'r') as zf, apk_path.open('wb+') as of:
            of.write(zf.read('universal.apk'))
        self.logger.info(f'Extracted {apk_path}')
        return apk_path


if __name__ == '__main__':
    BundleTool.invoke_cli()
