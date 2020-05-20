import pathlib
import zipfile
from typing import List
from typing import Optional
from typing import Union

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
    BUNDLE_PATH = cli.ArgumentProperties(
        flags=('--bundle',),
        key='aab_path',
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to Android app bundle file',
        argparse_kwargs={
            'required': True,
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
    DUMP_TARGET = cli.ArgumentProperties(
        key='target',
        description='Target of the dump',
        argparse_kwargs={
            'choices': ['manifest', 'resources', 'config']
        }
    )
    DUMP_XPATH = cli.ArgumentProperties(
        flags=('--xpath',),
        key='xpath',
        description=(
            'XML path to specific attribute in the target. '
            'For example "/manifest/@android:versionCode" to obtain the version code from manifest. '
            'If not given, the full target will be dumped.'
        ),
        argparse_kwargs={
            'required': False,
        }
    )


KeystorePassword = Union[str, BundleToolTypes.KeystorePassword]
KeyAlias = Union[str, BundleToolTypes.KeyAlias]
KeyPassword = Union[str, BundleToolTypes.KeyPassword]


@cli.common_arguments()
class BundleTool(cli.CliApp, PathFinderMixin):
    """
    Manage Android App Bundles using Bundletool
    https://developer.android.com/studio/command-line/bundletool
    """

    def __init__(self, *args, **kwargs):
        super(BundleTool, self).__init__(*args, **kwargs)
        self._bundletool_jar_path: Optional[pathlib.Path] = None

    @property
    def _jar_path(self) -> pathlib.Path:
        if self._bundletool_jar_path is None:
            current_dir = pathlib.Path(__file__).parent.resolve()
            binaries_dir = current_dir.parent.parent.parent / 'bin'
            bundletool_jar = next(binaries_dir.glob('bundletool*.jar'), None)
            if not bundletool_jar:
                raise IOError(f'BundleTool jar not available in {current_dir}')
            self._bundletool_jar_path = bundletool_jar.resolve()
        return self._bundletool_jar_path

    @classmethod
    def _get_password_value(cls, password: Optional[Union[KeyPassword, KeystorePassword]]):
        if password is None:
            return None
        elif isinstance(password, str):
            return password
        elif isinstance(password, (BundleToolTypes.KeystorePassword, BundleToolTypes.KeyPassword)):
            return password.value
        raise TypeError(f'Invalid type {type(password)} for password')

    @classmethod
    def _convert_cli_args_to_signing_info(
            cls,
            keystore_path: Optional[pathlib.Path] = None,
            keystore_password: Optional[KeystorePassword] = None,
            key_alias: Optional[KeyAlias] = None,
            key_password: Optional[KeyPassword] = None) -> Optional[AndroidSigningInfo]:
        keystore_password_value = cls._get_password_value(keystore_password)
        key_password_value = cls._get_password_value(key_password)
        if keystore_path and keystore_password_value and key_alias and key_password_value:
            return AndroidSigningInfo(
                store_path=keystore_path,
                store_pass=keystore_password_value,
                key_alias=str(key_alias),
                key_pass=key_password_value)
        elif keystore_path or keystore_password_value or key_alias or key_password_value:
            error_msg = 'Either all signing info arguments should be specified, or none of them should'
            raise BundleToolArgument.KEYSTORE_PATH.raise_argument_error(error_msg)
        else:
            return None

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
            keystore_password: Optional[KeystorePassword] = None,
            key_alias: Optional[KeyAlias] = None,
            key_password: Optional[KeyPassword] = None,
            mode: Optional[str] = None,
            should_print: bool = True) -> List[pathlib.Path]:
        """
        Generates an APK Set archive containing either all possible split APKs and
        standalone APKs or APKs optimized for the connected device (see connected-
        device flag). Returns list of generated APK set archives.
        """
        signing_info = self._convert_cli_args_to_signing_info(
            keystore_path, keystore_password, key_alias, key_password)

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
            keystore_password: Optional[KeystorePassword] = None,
            key_alias: Optional[KeyAlias] = None,
            key_password: Optional[KeyPassword] = None) -> List[pathlib.Path]:
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

    @cli.action('dump',
                BundleToolArgument.DUMP_TARGET,
                BundleToolArgument.BUNDLE_PATH,
                BundleToolArgument.DUMP_XPATH)
    def dump(self, target: str, aab_path: pathlib.Path, xpath: Optional[str] = None) -> str:
        """
        Get files list or extract values from the bundle in a human-readable form.
        """
        if xpath:
            self.logger.info(f'Dump attribute "{xpath}" from target "{target}" from {aab_path}')
        else:
            self.logger.info(f'Dump target "{target}" from {aab_path}')

        command = [
            'java', '-jar', str(self._jar_path),
            'dump', target, '--bundle', aab_path
        ]
        if xpath:
            command.extend(['--xpath', xpath])

        process = self.execute(command)
        if process.returncode != 0:
            raise BundleToolError(f'Unable to dump {target} for bundle {aab_path}', process)
        return process.stdout

    @cli.action('validate', BundleToolArgument.BUNDLE_PATH, )
    def validate(self, aab_path: pathlib.Path) -> str:
        """
        Verify that given Android App Bundle is valid and print
        out information about it.
        """
        self.logger.info(f'Validate {aab_path}')
        command = [
            'java', '-jar', str(self._jar_path),
            'validate', '--bundle', aab_path
        ]
        process = self.execute(command)
        if process.returncode != 0:
            raise BundleToolError(f'Unable to validate bundle {aab_path}', process)
        return process.stdout

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

    def _build_apk_set_archive(self,
                               aab_path: pathlib.Path,
                               *,
                               signing_info: Optional[AndroidSigningInfo] = None,
                               mode: Optional[str] = None) -> pathlib.Path:
        self.logger.info(f'Generating APKs from bundle {aab_path}')
        apks_path = aab_path.parent / f'{aab_path.stem}.apks'
        command = [
            'java', '-jar', str(self._jar_path),
            'build-apks',
            '--bundle', str(aab_path),
            '--output', str(apks_path),
            *(['--mode', mode] if mode else []),
        ]
        if signing_info:
            store_pass_arg = f'pass:{signing_info.store_pass}'
            key_pass_arg = f'pass:{signing_info.key_pass}'
            command.extend([
                '--ks', str(signing_info.store_path),
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
