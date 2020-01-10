#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import shutil
from tempfile import NamedTemporaryFile
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
        argparse_kwargs={'required': False}
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
        }
    )
    CERTIFICATE_PASSWORD = cli.ArgumentProperties(
        flags=('--certificate-password',),
        key='certificate_password',
        type=Password,
        description='Encrypted p12 certificate password',
        argparse_kwargs={'required': False, 'default': ''},
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
        Create a macOS keychain, add it to the search list.
        """

        self.logger.info(f'Create keychain {self.path}')
        process = self.execute(
            ('security', 'create-keychain', '-p', password.value, self.path),
            obfuscate_patterns=[password.value])
        if process.returncode != 0:
            raise KeychainError(f'Unable to create keychain {self.path}', process)

        process = self.execute(('security', 'list-keychains', '-d', 'user', '-s', 'login.keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to add keychain {self.path} to keychain search list', process)

        os.chmod(str(self.path), 0o600)
        return self.path

    @cli.action('delete')
    def delete(self):
        """
        Delete keychains and remove them from the search list.
        """

        self.logger.info(f'Delete keychain {self.path}')
        process = self.execute(('security', 'delete-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Failed to delete keychain {self.path}', process)

    @cli.action('show-info')
    def show_info(self):
        """
        Show all settings for the keychain.
        """

        self.logger.info(f'Keychain {self.path} settings:')
        process = self.execute(('security', 'show-keychain-info', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Failed to show information for keychain {self.path}', process)

    @cli.action('set-timeout', KeychainArgument.TIMEOUT)
    def set_timeout(self, timeout: Optional[Seconds] = None):
        """
        Set timeout settings for the keychain.
        If seconds are not provided, then no-timeout will be set.
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
        Lock the specified keychain.
        """

        self.logger.info(f'Lock keychain {self.path}')
        process = self.execute(('security', 'lock-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to unlock keychain {self.path}', process)

    @cli.action('unlock', KeychainArgument.PASSWORD)
    def unlock(self, password: Password = Password('')):
        """
        Unlock the specified keychain.
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
        Show the system default keychain.
        """

        self.logger.info(f'Get system default keychain')
        default = self._get_default()
        self.echo(default)
        return default

    def _get_default(self):
        process = self.execute(('security', 'default-keychain'), show_output=False)
        if process.returncode != 0:
            raise KeychainError(f'Unable to get default keychain', process)
        cleaned = process.stdout.strip().strip('"').strip("'")
        return pathlib.Path(cleaned)

    @cli.action('make-default')
    def make_default(self):
        """
        Set the keychain as the system default keychain.
        """

        self.logger.info(f'Set keychain {self.path} to system default keychain')
        process = self.execute(('security', 'default-keychain', '-s', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to set {self.path} as default keychain', process)

    @cli.action('initialize', KeychainArgument.PASSWORD, KeychainArgument.TIMEOUT)
    def initialize(self, password: Password = Password(''), timeout: Optional[Seconds] = None) -> Keychain:
        """
        Set up the keychain to be used for code signing. Create the keychain
        at specified path with specified password with given timeout.
        Make it default and unlock it for upcoming use.
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
        List available code signing certificates in specified keychain.
        """

        self.logger.info(f'List available code signing certificates in keychain {self.path}')
        all_certificates = self._find_certificates()
        certificates = [cert for cert in all_certificates if cert.is_code_signing_certificate()]
        if should_print:
            self.echo(json.dumps(certificates, sort_keys=True, indent=4))
        return certificates

    def _generate_path(self):
        with NamedTemporaryFile(prefix='build_', suffix='.keychain') as tf:
            self._path = pathlib.Path(tf.name)

    @cli.action('add-certificates',
                KeychainArgument.CERTIFICATE_PATHS,
                KeychainArgument.CERTIFICATE_PASSWORD)
    def add_certificates(self,
                         certificate_path_patterns: Sequence[pathlib.Path],
                         certificate_password: Password = Password('')):
        """
        Add p12 certificate to specified keychain.
        """

        self.logger.info(f'Add certificates to keychain {self.path}')
        certificate_paths = list(self.find_paths(*certificate_path_patterns))
        if not certificate_paths:
            raise KeychainError('Did not find any certificates from specified locations')
        for certificate_path in certificate_paths:
            self._add_certificate(certificate_path, certificate_password)

    def _add_certificate(self,
                         certificate_path: pathlib.Path,
                         certificate_password: Optional[Password] = None):
        self.logger.info(f'Add certificate {certificate_path} to keychain {self.path}')
        # If case of no password, we need to explicitly set -P '' flag. Otherwise,
        # security tries to open an interactive dialog to prompt the user for a password,
        # which fails in non-interactive CI environment.
        if certificate_password is not None:
            obfuscate_patterns = [certificate_password.value]
        else:
            certificate_password = Password('')
            obfuscate_patterns = []

        process = self.execute([
            'security', 'import', certificate_path,
            '-f', "pkcs12",
            '-k', self.path,
            '-T', shutil.which('codesign'),
            '-P', certificate_password.value,
        ], obfuscate_patterns=obfuscate_patterns)
        if process.returncode != 0:
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
