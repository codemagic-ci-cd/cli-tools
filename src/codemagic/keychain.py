#!/usr/bin/env python3

import argparse
import json
import os
import pathlib
import sys
from typing import Optional

from . import cli
from . import models


class Seconds(int):
    pass


class Password(cli.EnvironmentArgumentValue):
    @classmethod
    def _is_valid(cls, value: str) -> bool:
        return True


class KeychainError(cli.CliAppException):
    pass


class KeychainArgument(cli.Argument):
    PATH = cli.ArgumentProperties(
        key='keychain_path',
        type=pathlib.Path,
        description='Keychain path',
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
    CERTIFICATE_PATH = cli.ArgumentProperties(
        flags=('-c', '--certificate'),
        key='certificate_path',
        type=pathlib.Path,
        description='Path to p12 certificate',
        argparse_kwargs={'required': True},
    )
    CERTIFICATE_PASSWORD = cli.ArgumentProperties(
        flags=('--certificate-password',),
        key='certificate_password',
        type=Password,
        description='Encrypted p12 certificate password',
        argparse_kwargs={'required': False, 'default': ''},
    )


@cli.common_arguments(KeychainArgument.PATH)
class Keychain(cli.CliApp):
    """
    Utility to manage macOS keychains and certificates
    """

    def __init__(self, path: pathlib.Path):
        super().__init__()
        self.path = path

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        path = KeychainArgument.PATH.from_args(cli_args)
        return Keychain(path)

    @cli.action('create', KeychainArgument.PASSWORD)
    def create(self, password: Password = Password('')):
        """
        Create a macOS keychain, add it to the search list.
        """
        process = self.execute(
            ('security', 'create-keychain', '-p', password.value, self.path),
            obfuscate_patterns=[password.value])
        if process.returncode != 0:
            raise KeychainError(f'Unable to create keychain {self.path}', process)

        process = self.execute(('security', 'list-keychains', '-d', 'user', '-s', 'login.keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to add keychain {self.path} to keychain search list', process)

        os.chmod(str(self.path), 0o600)

    @cli.action('delete')
    def delete(self):
        """
        Delete keychains and remove them from the search list.
        """
        process = self.execute(('security', 'delete-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Failed to delete keychain {self.path}', process)

    @cli.action('show-info')
    def show_info(self):
        """
        Show all settings for the keychain.
        """
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
        process = self.execute(cmd_args)
        if process.returncode != 0:
            raise KeychainError(f'Unable to set timeout to the keychain {self.path}', process)

    @cli.action('lock')
    def lock(self):
        """
        Lock the specified keychain.
        """
        process = self.execute(('security', 'lock-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to unlock keychain {self.path}', process)

    @cli.action('unlock', KeychainArgument.PASSWORD)
    def unlock(self, password: Password = Password('')):
        """
        Unlock the specified keychain.
        """
        process = self.execute(
            ('security', 'unlock-keychain', '-p', password.value, self.path),
            obfuscate_patterns=[password.value])
        if process.returncode != 0:
            raise KeychainError(f'Unable to unlock keychain {self.path}', process)

    @cli.action('make-default')
    def make_default(self):
        """
        Set the keychain as the system default keychain.
        """
        process = self.execute(('security', 'default-keychain', '-s', self.path))
        if process.returncode != 0:
            raise KeychainError(f'Unable to set {self.path} as default keychain', process)

    @cli.action('initialize', KeychainArgument.PASSWORD, KeychainArgument.TIMEOUT)
    def initialize(self, password: Password = Password(''), timeout: Optional[Seconds] = None):
        """
        Set up the keychain to be used for code signing. Create the keychain
        at specified path with specified password with given timeout.
        Make it default and unlock it for upcoming use.
        """
        self.create(password)
        self.set_timeout(timeout=timeout)
        self.make_default()
        self.unlock(password)
        self.show_info()

    @cli.action('list-certificates')
    def list_code_signing_certificates(self):
        """
        List available code signing certificates in specified keychain.
        """
        certificates = [
            certificate for certificate in self.find_certificates()
            if certificate.is_code_signign_certificate()
        ]
        json.dump(certificates, sys.stdout, sort_keys=True, indent=4)

    @cli.action('add-certificate',
                KeychainArgument.CERTIFICATE_PATH,
                KeychainArgument.CERTIFICATE_PASSWORD)
    def add_certificate(self, certificate_path: pathlib.Path, certificate_password: Optional[Password] = None):
        """
        Add p12 certificate to specified keychain.
        """
        # If case of no password, we need to explicitly set -P '' flag. Otherwise,
        # security tries to open an interactive dialog to prompt the user for a password,
        # which fails in non-interactive CI environment.
        if certificate_password is not None:
            obfuscate_patterns = [certificate_password.value]
        else:
            certificate_password = Password('')
            obfuscate_patterns = []

        process = self.execute([
            'security', "import", certificate_path,
            "-f", "pkcs12",
            "-k", self.path,
            "-T", 'codesign',
            "-P", certificate_password.value,
        ], obfuscate_patterns=obfuscate_patterns)
        if process.returncode != 0:
            raise KeychainError(f'Unable to add certificate {certificate_path} to keychain {self.path}', process)

    def find_certificates(self):
        process = self.execute(('security', 'find-certificate', '-a', '-p', self.path), show_output=False)
        if process.returncode != 0:
            raise KeychainError(f'Unable to list certificates from keychain {self.path}', process)

        pem = ''
        for line in process.stdout.splitlines():
            pem += line + '\n'
            if line == '-----END CERTIFICATE-----':
                yield models.Certificate(pem)
                pem = ''


if __name__ == '__main__':
    Keychain.invoke_cli()
