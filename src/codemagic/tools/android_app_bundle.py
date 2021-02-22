import pathlib
import shutil
import zipfile
from typing import List
from typing import Optional
from typing import Union
from typing import overload

import codemagic
from codemagic import cli
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo


class AndroidAppBundleTypes:
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


class AndroidAppBundleError(cli.CliAppException):
    pass


class AndroidAppBundleArgument(cli.Argument):
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
    KEYSTORE_PATH_REQUIRED = KEYSTORE_PATH.duplicate(argparse_kwargs={'required': True})
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        flags=('--ks-pass',),
        key='keystore_password',
        type=AndroidAppBundleTypes.KeystorePassword,
        description='Keystore password',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEYSTORE_PASSWORD_REQUIRED = KEYSTORE_PASSWORD.duplicate(argparse_kwargs={'required': True})
    KEY_ALIAS = cli.ArgumentProperties(
        flags=('--ks-key-alias',),
        key='key_alias',
        type=AndroidAppBundleTypes.KeyAlias,
        description='Keystore key alias',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEY_ALIAS_REQUIRED = KEY_ALIAS.duplicate(argparse_kwargs={'required': True})
    KEY_PASSWORD = cli.ArgumentProperties(
        flags=('--key-pass',),
        key='key_password',
        type=AndroidAppBundleTypes.KeyPassword,
        description='Keystore key password',
        argparse_kwargs={
            'default': None,
            'required': False,
        },
    )
    KEY_PASSWORD_REQUIRED = KEY_PASSWORD.duplicate(argparse_kwargs={'required': True})
    BUILD_APKS_MODE = cli.ArgumentProperties(
        flags=('--mode',),
        key='mode',
        description=(
            'Set the mode to universal if you want bundletool to build only a single APK '
            "that includes all of your app's code and resources such that the APK is "
            'compatible with all device configurations your app supports.'
        ),
        argparse_kwargs={
            'default': None,
            'required': False,
            'choices': ['universal'],
        },
    )
    DUMP_TARGET = cli.ArgumentProperties(
        key='target',
        description='Target of the dump',
        argparse_kwargs={
            'choices': ['manifest', 'resources', 'config'],
        },
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
        },
    )


KeystorePassword = Union[str, AndroidAppBundleTypes.KeystorePassword]
KeyAlias = Union[str, AndroidAppBundleTypes.KeyAlias]
KeyPassword = Union[str, AndroidAppBundleTypes.KeyPassword]


@cli.common_arguments()
class AndroidAppBundle(cli.CliApp, PathFinderMixin):
    """
    Manage Android App Bundles using
    [Bundletool](https://developer.android.com/studio/command-line/bundletool)
    """

    def __init__(self, *args, **kwargs):
        super(AndroidAppBundle, self).__init__(*args, **kwargs)
        self.__bundletool_jar: Optional[pathlib.Path] = None

    @property
    def _bundletool_jar(self) -> pathlib.Path:
        if self.__bundletool_jar is None:
            data_dir = pathlib.Path(codemagic.__file__).parent / 'data'
            bundletool_jar = next(data_dir.rglob('bundletool*.jar'), None)
            if not bundletool_jar:
                raise IOError(f'Bundletool jar not available in {data_dir}')
            self.__bundletool_jar = bundletool_jar.resolve()
        return self.__bundletool_jar

    @classmethod
    def _ensure_jarsigner(cls):
        if shutil.which('jarsigner') is None:
            raise IOError('Missing executable "jarsigner"')

    @classmethod
    @overload
    def _get_password_value(cls, password: Union[KeyPassword, KeystorePassword]) -> str:
        ...

    @classmethod
    @overload
    def _get_password_value(cls, password: None) -> None:
        ...

    @classmethod
    def _get_password_value(cls, password: Optional[Union[KeyPassword, KeystorePassword]]) -> Optional[str]:
        if password is None:
            return None
        elif isinstance(password, str):
            return password
        elif isinstance(password, (AndroidAppBundleTypes.KeystorePassword, AndroidAppBundleTypes.KeyPassword)):
            return password.value
        raise TypeError(f'Invalid type {type(password)} for password')

    @classmethod
    @overload
    def _convert_cli_args_to_signing_info(
            cls,
            keystore_path: pathlib.Path,
            keystore_password: KeystorePassword,
            key_alias: KeyAlias,
            key_password: KeyPassword) -> AndroidSigningInfo:
        ...

    @classmethod
    @overload
    def _convert_cli_args_to_signing_info(
            cls,
            keystore_path: Optional[pathlib.Path],
            keystore_password: Optional[KeystorePassword],
            key_alias: Optional[KeyAlias],
            key_password: Optional[KeyPassword]) -> Optional[AndroidSigningInfo]:
        ...

    @classmethod
    def _convert_cli_args_to_signing_info(
            cls,
            keystore_path: Optional[pathlib.Path],
            keystore_password: Optional[KeystorePassword],
            key_alias: Optional[KeyAlias],
            key_password: Optional[KeyPassword]) -> Optional[AndroidSigningInfo]:
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
            raise AndroidAppBundleArgument.KEYSTORE_PATH.raise_argument_error(error_msg)
        else:
            return None

    def _get_aab_paths_from_pattern(self, pattern: pathlib.Path) -> List[pathlib.Path]:
        def is_valid_aab(aab_path):  # Exclude intermediate Android app bundles
            return 'intermediates' not in aab_path.parts

        if pattern.is_file():  # No need to glob in case of verbatim path
            aab_paths = [pattern]
        else:
            aab_paths = [aab for aab in self.find_paths(pattern) if is_valid_aab(aab)]
            if not aab_paths:
                error_msg = 'Did not find any matching Android app bundles from which to generate APKs'
                raise AndroidAppBundleError(error_msg)
            self.logger.info(f'Found {len(aab_paths)} matching files')

        return aab_paths

    @cli.action('build-apks',
                AndroidAppBundleArgument.BUNDLE_PATTERN,
                AndroidAppBundleArgument.KEYSTORE_PATH,
                AndroidAppBundleArgument.KEYSTORE_PASSWORD,
                AndroidAppBundleArgument.KEY_ALIAS,
                AndroidAppBundleArgument.KEY_PASSWORD,
                AndroidAppBundleArgument.BUILD_APKS_MODE)
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
        device flag). Returns list of generated APK set archives
        """
        signing_info = self._convert_cli_args_to_signing_info(
            keystore_path, keystore_password, key_alias, key_password)

        apks_paths = []
        for aab_path in self._get_aab_paths_from_pattern(aab_pattern):
            apks_path = self._build_apk_set_archive(aab_path, signing_info=signing_info, mode=mode)
            apks_paths.append(apks_path)
            if should_print:
                self.echo(str(apks_path))
        return apks_paths

    @cli.action('build-universal-apk',
                AndroidAppBundleArgument.BUNDLE_PATTERN,
                AndroidAppBundleArgument.KEYSTORE_PATH,
                AndroidAppBundleArgument.KEYSTORE_PASSWORD,
                AndroidAppBundleArgument.KEY_ALIAS,
                AndroidAppBundleArgument.KEY_PASSWORD)
    def build_universal_apks(
            self,
            aab_pattern: pathlib.Path,
            keystore_path: Optional[pathlib.Path] = None,
            keystore_password: Optional[KeystorePassword] = None,
            key_alias: Optional[KeyAlias] = None,
            key_password: Optional[KeyPassword] = None) -> List[pathlib.Path]:
        """
        Shortcut for `build-apks` to build universal APKs from bundles
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
                AndroidAppBundleArgument.DUMP_TARGET,
                AndroidAppBundleArgument.BUNDLE_PATH,
                AndroidAppBundleArgument.DUMP_XPATH)
    def dump(self, target: str, aab_path: pathlib.Path, xpath: Optional[str] = None) -> str:
        """
        Get files list or extract values from the bundle in a human-readable form
        """
        if xpath:
            self.logger.info(f'Dump attribute "{xpath}" from target "{target}" from {aab_path}')
        else:
            self.logger.info(f'Dump target "{target}" from {aab_path}')

        command = [
            'java', '-jar', str(self._bundletool_jar),
            'dump', target, '--bundle', aab_path,
        ]
        if xpath:
            command.extend(['--xpath', xpath])

        process = self.execute(command)
        if process.returncode != 0:
            raise AndroidAppBundleError(f'Unable to dump {target} for bundle {aab_path}', process)
        return process.stdout

    @cli.action('sign',
                AndroidAppBundleArgument.BUNDLE_PATH,
                AndroidAppBundleArgument.KEYSTORE_PATH_REQUIRED,
                AndroidAppBundleArgument.KEYSTORE_PASSWORD_REQUIRED,
                AndroidAppBundleArgument.KEY_ALIAS_REQUIRED,
                AndroidAppBundleArgument.KEY_PASSWORD_REQUIRED)
    def sign(self,
             aab_path: pathlib.Path,
             keystore_path: pathlib.Path,
             keystore_password: KeystorePassword,
             key_alias: KeyAlias,
             key_password: KeyPassword):
        """
        Sign Android app bundle with specified key and keystore
        """
        self._ensure_jarsigner()
        signing_info = self._convert_cli_args_to_signing_info(
            keystore_path, keystore_password, key_alias, key_password)

        self.logger.info(f'Sign {aab_path}')
        command = [
            'jarsigner', '-verbose',
            '-sigalg', 'SHA1withRSA',
            '-digestalg', 'SHA1',
            '-keystore', str(signing_info.store_path),
            '-storepass', signing_info.store_pass,
            '-keypass', signing_info.key_pass,
            str(aab_path),
            signing_info.key_alias,
        ]
        obfuscate_patterns = [signing_info.store_pass, signing_info.key_pass]
        process = self.execute(command, obfuscate_patterns=obfuscate_patterns, show_output=False)
        if process.returncode != 0:
            raise AndroidAppBundleError(f'Unable to sign bundle {aab_path}', process)

    @cli.action('is-signed', AndroidAppBundleArgument.BUNDLE_PATH)
    def is_signed(self, aab_path: pathlib.Path):
        """ Check if given Android app bundle is signed """
        self._ensure_jarsigner()
        command = ['jarsigner', '-verbose', '-verify', str(aab_path)]
        process = self.execute(command, show_output=False)
        if 'jar is unsigned' in process.stdout:
            raise AndroidAppBundleError(f'Bundle {aab_path} is not signed')
        self.echo(f'Bundle {aab_path} is signed')

    @cli.action('validate', AndroidAppBundleArgument.BUNDLE_PATH)
    def validate(self, aab_path: pathlib.Path) -> str:
        """
        Verify that given Android App Bundle is valid and print out information about it
        """
        self.logger.info(f'Validate {aab_path}')
        command = [
            'java', '-jar', str(self._bundletool_jar),
            'validate', '--bundle', aab_path,
        ]
        process = self.execute(command)
        if process.returncode != 0:
            raise AndroidAppBundleError(f'Unable to validate bundle {aab_path}', process)
        return process.stdout

    @cli.action('bundletool-version')
    def bundletool_version(self) -> str:
        """ Get Bundletool version """
        self.logger.info('Get Bundletool version')
        process = self.execute(('java', '-jar', str(self._bundletool_jar), 'version'), show_output=False)
        if process.returncode != 0:
            raise AndroidAppBundleError('Unable to get Bundletool version', process)
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
            'java', '-jar', str(self._bundletool_jar),
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
            raise AndroidAppBundleError(f'Unable to generate apks file for bundle {aab_path}', process)
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
    AndroidAppBundle.invoke_cli()
