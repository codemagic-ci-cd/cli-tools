#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import shutil
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import Certificate


class Seconds(int):
    pass


class Password(cli.EnvironmentArgumentValue[str]):
    @classmethod
    def _is_valid(cls, value: str) -> bool:
        return True


class KeychainError(cli.CliAppException):
    pass


class KeychainArgument(cli.Argument):
    PATH = cli.ArgumentProperties(
        flags=('-p', '--path'),
        key='path',
        type=pathlib.Path,
        description=(
            'Keychain path. If not provided, the system default '
            'keychain will be used instead'
        ),
        argparse_kwargs={'required': False},
    )
    PASSWORD = cli.ArgumentProperties(
        flags=('-pw', '--password'),
        key='password',
        type=Password,
        description='Keychain password',
        argparse_kwargs={'required': False, 'default': ''},
    )
    TIMEOUT = cli.ArgumentProperties(
        flags=('-t', '--timeout'),
        key='timeout',
        type=Seconds,
        description='Keychain timeout in seconds, defaults to no timeout',
        argparse_kwargs={'required': False, 'default': None},
    )
    CERTIFICATE_PATHS = cli.ArgumentProperties(
        flags=('-c', '--certificate'),
        key='certificate_path_patterns',
        type=pathlib.Path,
        description=(
            'Path to pkcs12 certificate. Can be either a path literal, or '
            'a glob pattern to match certificates.'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'certificate-path',
            'default': (Certificate.DEFAULT_LOCATION / '*.p12',),
        },
    )
    CERTIFICATE_PASSWORD = cli.ArgumentProperties(
        flags=('--certificate-password',),
        key='certificate_password',
        type=Password,
        description='Encrypted p12 certificate password',
        argparse_kwargs={'required': False, 'default': ''},
    )
    ALLOWED_APPLICATIONS = cli.ArgumentProperties(
        flags=('-a', '--allow-app'),
        key='allowed_applications',
        description='Specify an application which may access the imported key without warning',
        type=pathlib.Path,
        argparse_kwargs={
            'required': False,
            'default': (pathlib.Path('codesign'), pathlib.Path('productsign')),
            'nargs': '+',
            'metavar': 'allowed-app',
        },
    )
    ALLOW_ALL_APPLICATIONS = cli.ArgumentProperties(
        flags=('-A', '--allow-all-applications'),
        key='allow_all_applications',
        type=bool,
        description='Allow any application to access the imported key without warning',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    DISALLOW_ALL_APPLICATIONS = cli.ArgumentProperties(
        flags=('-D', '--disallow-all-applications'),
        key='disallow_all_applications',
        type=bool,
        description='Do not allow any applications to access the imported key without warning',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


@cli.common_arguments(KeychainArgument.PATH)
class Keychain(cli.CliApp, PathFinderMixin):
    """
    Utility to manage macOS keychains and certificates
    """

    def __init__(self, path: Optional[pathlib.Path] = None, **kwargs):
        super().__init__(**kwargs)
        self._path = path

    @property
    def path(self) -> pathlib.Path:
        if self._path is None:
            self._path = self._get_default()
        return self._path

    @cli.action('create', KeychainArgument.PASSWORD)
    def create(self, password: Password = Password('')) -> pathlib.Path:
        """
        Create a macOS keychain, add it to the search list
        """

        self.logger.info(f'Create keychain {self.path}')
        process = self.execute(
            ('security', 'create-keychain', '-p', password.value, self.path),
            obfuscate_patterns=[password.value])
        if process.returncode != 0:
            raise KeychainError(f'Unable to create keychain {self.path}', process)

        if not self.path.exists():
            # In some cases `security` adds a '-db' suffix to the keychain name
            self._path = pathlib.Path(f'{self.path}-db')
        if not self.path.exists():
            raise KeychainError('Keychain was not created')

        process = self.execute(('security', 'list-keychains', '-d', 'user', '-s', 'login.keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to add keychain {self.path} to keychain search list', process)

        os.chmod(str(self.path), 0o600)
        return self.path

    @cli.action('delete')
    def delete(self):
        """
        Delete keychains and remove them from the search list
        """

        self.logger.info(f'Delete keychain {self.path}')
        process = self.execute(('security', 'delete-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Failed to delete keychain {self.path}', process)

    @cli.action('show-info')
    def show_info(self):
        """
        Show all settings for the keychain
        """

        self.logger.info(f'Keychain {self.path} settings:')
        process = self.execute(('security', 'show-keychain-info', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Failed to show information for keychain {self.path}', process)

    @cli.action('set-timeout', KeychainArgument.TIMEOUT)
    def set_timeout(self, timeout: Optional[Seconds] = None):
        """
        Set timeout settings for the keychain.
        If seconds are not provided, then no-timeout will be set
        """

        cmd_args = ['security', 'set-keychain-settings', str(self.path)]
        if timeout is not None:
            cmd_args[-1:-1] = ['-t', str(timeout)]
            self.logger.info(f'Set keychain {self.path} timeout to {timeout} seconds')
        else:
            self.logger.info(f'Set keychain {self.path} timeout to "no timeout"')
        process = self.execute(cmd_args)
        if process.returncode != 0:
            raise KeychainError(f'Unable to set timeout to the keychain {self.path}', process)

    @cli.action('lock')
    def lock(self):
        """
        Lock the specified keychain
        """

        self.logger.info(f'Lock keychain {self.path}')
        process = self.execute(('security', 'lock-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to unlock keychain {self.path}', process)

    @cli.action('unlock', KeychainArgument.PASSWORD)
    def unlock(self, password: Password = Password('')):
        """
        Unlock the specified keychain
        """

        self.logger.info(f'Unlock keychain {self.path}')
        process = self.execute(
            ('security', 'unlock-keychain', '-p', password.value, self.path),
            obfuscate_patterns=[password.value])
        if process.returncode != 0:
            raise KeychainError(f'Unable to unlock keychain {self.path}', process)

    @cli.action('get-default')
    def get_default(self) -> pathlib.Path:
        """
        Show the system default keychain
        """

        self.logger.info('Get system default keychain')
        default = self._get_default()
        self.echo(str(default))
        return default

    def _get_default(self):
        process = self.execute(('security', 'default-keychain'), show_output=False)
        if process.returncode != 0:
            raise KeychainError('Unable to get default keychain', process)
        cleaned = process.stdout.strip().strip('"').strip("'")
        return pathlib.Path(cleaned)

    @cli.action('make-default')
    def make_default(self):
        """
        Set the keychain as the system default keychain
        """

        self.logger.info(f'Set keychain {self.path} to system default keychain')
        process = self.execute(('security', 'default-keychain', '-s', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to set {self.path} as default keychain', process)

    @cli.action('use-login')
    def use_login_keychain(self) -> Keychain:
        """
        Use login keychain as the default keychain
        """

        keychains_root = pathlib.Path('~/Library/Keychains/').expanduser()
        for keychain_name in ('login.keychain-db', 'login.keychain'):
            keychain_path = keychains_root / keychain_name
            if keychain_path.is_file():
                self._path = keychain_path
                break
        else:
            raise KeychainError(f'Login keychain not found from {keychains_root}')

        self.logger.info(Colors.GREEN('Use login keychain %s as system default keychain'), self.path)
        self.make_default()
        return self

    @cli.action('initialize', KeychainArgument.PASSWORD, KeychainArgument.TIMEOUT)
    def initialize(self, password: Password = Password(''), timeout: Optional[Seconds] = None) -> Keychain:
        """
        Set up the keychain to be used for code signing. Create the keychain
        at specified path with specified password with given timeout.
        Make it default and unlock it for upcoming use
        """

        if not self._path:
            self._generate_path()

        message = f'Initialize new keychain to store code signing certificates at {self.path}'
        self.logger.info(Colors.GREEN(message))
        self.create(password)
        self.set_timeout(timeout=timeout)
        self.make_default()
        self.unlock(password)
        return self

    @cli.action('list-certificates')
    def list_code_signing_certificates(self, should_print: bool = True) -> List[Certificate]:
        """
        List available code signing certificates in specified keychain
        """

        self.logger.info(f'List available code signing certificates in keychain {self.path}')
        all_certificates = self._find_certificates()
        certificates = [cert for cert in all_certificates if cert.is_code_signing_certificate()]
        if should_print:
            self.echo(json.dumps(certificates, sort_keys=True, indent=4))
        return certificates

    def _generate_path(self):
        keychain_dir = pathlib.Path('~/Library/codemagic-cli-tools/keychains').expanduser()
        keychain_dir.mkdir(parents=True, exist_ok=True)
        date = datetime.now().strftime('%d-%m-%y')
        with NamedTemporaryFile(prefix=f'{date}_', suffix='.keychain-db', dir=keychain_dir) as tf:
            self._path = pathlib.Path(tf.name)

    @cli.action('add-certificates',
                KeychainArgument.CERTIFICATE_PATHS,
                KeychainArgument.CERTIFICATE_PASSWORD,
                KeychainArgument.ALLOWED_APPLICATIONS,
                KeychainArgument.ALLOW_ALL_APPLICATIONS,
                KeychainArgument.DISALLOW_ALL_APPLICATIONS)
    def add_certificates(
            self,
            certificate_path_patterns: Sequence[pathlib.Path] = KeychainArgument.CERTIFICATE_PATHS.get_default(),
            certificate_password: Password = Password(''),
            allowed_applications: Sequence[pathlib.Path] = KeychainArgument.ALLOWED_APPLICATIONS.get_default(),
            allow_all_applications: Optional[bool] = KeychainArgument.ALLOW_ALL_APPLICATIONS.get_default(),
            disallow_all_applications: Optional[bool] = KeychainArgument.DISALLOW_ALL_APPLICATIONS.get_default()):
        """
        Add p12 certificate to specified keychain
        """

        add_for_all_apps = False
        add_for_apps: List[str] = []
        if allow_all_applications and disallow_all_applications:
            raise KeychainArgument.ALLOW_ALL_APPLICATIONS.raise_argument_error(
                f'Using mutually exclusive options '
                f'{KeychainArgument.ALLOWED_APPLICATIONS.flag!r} and '
                f'{KeychainArgument.DISALLOW_ALL_APPLICATIONS.flag!r}')
        elif allow_all_applications:
            add_for_all_apps = True
        elif not disallow_all_applications:
            add_for_apps = list(self._get_certificate_allowed_applications(allowed_applications))

        self.logger.info('Add certificates to keychain %s', self.path)
        certificate_paths = list(self.find_paths(*certificate_path_patterns))
        if not certificate_paths:
            raise KeychainError('Did not find any certificates from specified locations')
        for certificate_path in certificate_paths:
            self._add_certificate(certificate_path, certificate_password, add_for_all_apps, add_for_apps)

    @classmethod
    def _get_certificate_allowed_applications(
            cls, given_allowed_applications: Sequence[pathlib.Path]) -> Iterable[str]:
        for application in given_allowed_applications:
            resolved_path = shutil.which(application)
            if resolved_path is None:
                # Only raise exception if user-specified path is not present
                if application not in KeychainArgument.ALLOWED_APPLICATIONS.get_default():
                    raise KeychainArgument.ALLOWED_APPLICATIONS.raise_argument_error(
                        f'Application "{application}" does not exist or is not in PATH')
            else:
                yield str(resolved_path)

    def _add_certificate(self,
                         certificate_path: pathlib.Path,
                         certificate_password: Optional[Password] = None,
                         allow_for_all_apps: bool = False,
                         allowed_applications: Sequence[str] = tuple()):
        self.logger.info(f'Add certificate {certificate_path} to keychain {self.path}')
        # If case of no password, we need to explicitly set -P '' flag. Otherwise,
        # security tries to open an interactive dialog to prompt the user for a password,
        # which fails in non-interactive CI environment.
        if certificate_password is not None:
            obfuscate_patterns = [certificate_password.value]
        else:
            certificate_password = Password('')
            obfuscate_patterns = []

        import_cmd = [
            'security', 'import', certificate_path,
            '-f', 'pkcs12',
            '-k', self.path,
            '-P', certificate_password.value,
        ]
        if allow_for_all_apps:
            import_cmd.append('-A')
        for allowed_application in allowed_applications:
            import_cmd.extend(['-T', allowed_application])

        process = self.execute(import_cmd, obfuscate_patterns=obfuscate_patterns)

        if process.returncode != 0:
            if 'The specified item already exists in the keychain' in process.stderr:
                pass  # It is fine that the certificate is already in keychain
            else:
                raise KeychainError(f'Unable to add certificate {certificate_path} to keychain {self.path}', process)

    def _find_certificates(self):
        process = self.execute(('security', 'find-certificate', '-a', '-p', self.path), show_output=False)
        if process.returncode != 0:
            raise KeychainError(f'Unable to list certificates from keychain {self.path}', process)

        pem = ''
        for line in process.stdout.splitlines():
            pem += line + '\n'
            if line == '-----END CERTIFICATE-----':
                try:
                    yield Certificate.from_pem(pem)
                except ValueError:
                    self.logger.warning(Colors.YELLOW('Failed to read certificate from keychain'))
                pem = ''


if __name__ == '__main__':
    Keychain.invoke_cli()
