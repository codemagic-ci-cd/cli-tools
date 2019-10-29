#!/usr/bin/env python3

import argparse
import os
import pathlib
from typing import Optional

import cli


class Seconds(int):
    pass


class KeychainError(cli.CliAppException):
    pass


class KeychainArgument(cli.Argument):
    PATH = cli.ArgumentValue(
        key='path',
        description='Keychain path',
    )
    PASSWORD = cli.ArgumentValue(
        flags=('-pw', '--password'),
        key='password',
        description='Keychain password',
        argparse_kwargs={'required': True, 'default': None}
    )
    TIMEOUT = cli.ArgumentValue(
        flags=('-t', '--timeout'),
        key='timeout',
        type=Seconds,
        description='Keychain timeout in seconds, defaults to no timeout',
        argparse_kwargs={'required': False, 'default': None}
    )

    def is_action_kwarg(self):
        return self in (KeychainArgument.TIMEOUT,)


class Keychain(cli.CliApp):
    """
    Utility to manage macOS keychains and certificates
    """

    def __init__(self, path: pathlib.Path, password: Optional[str] = None):
        super().__init__()
        self.path = path
        self.password = password
        self.default_obfuscation = [password]

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        path = getattr(cli_args, KeychainArgument.PATH.value.key)
        password = getattr(cli_args, KeychainArgument.PASSWORD.value.key, KeychainArgument.PASSWORD.get_default())
        return Keychain(pathlib.Path(path), password=password)

    def __str__(self):
        return f'{self.__class__.__name__}(path="{self.path}", password="{"********" if self.password else ""}")'

    @cli.action('create', KeychainArgument.PATH, KeychainArgument.PASSWORD)
    def create(self):
        """
        Create a macOS keychain, add it to the search list.
        """
        process, command = self.execute(('security', 'create-keychain', '-p', self.password, self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to create keychain {self.path}', process.returncode)

        process, command = self.execute(('security', 'list-keychains', '-d', 'user', '-s', 'login.keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to add keychain {self.path} to keychain search list',
                                process.returncode)

        os.chmod(str(self.path), 0o600)

    @cli.action('delete', KeychainArgument.PATH)
    def delete(self):
        """
        Delete keychains and remove them from the search list.
        """
        process, command = self.execute(('security', 'delete-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Failed to delete keychain {self.path}', process.returncode)

    @cli.action('show-info', KeychainArgument.PATH)
    def show_info(self):
        """ Show all settings for the keychain. """
        process, command = self.execute(('security', 'show-keychain-info', self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Failed to show information for keychain {self.path}', process.returncode)

    @cli.action('set-timeout', KeychainArgument.PATH, KeychainArgument.TIMEOUT)
    def set_timeout(self, timeout: Optional[Seconds] = None):
        """
        Set timeout settings for the keychain.
        If seconds are not provided, then no-timeout will be set.
        """
        cmd_args = ['security', 'set-keychain-settings', str(self.path)]
        if timeout is not None:
            cmd_args[-1:-1] = ['-t', str(timeout)]
        process, command = self.execute(cmd_args)
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to set timeout to the keychain {self.path}', process.returncode)

    @cli.action('lock', KeychainArgument.PATH)
    def lock(self):
        """
        Lock the specified keychain.
        """
        process, command = self.execute(('security', 'lock-keychain', self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to unlock keychain {self.path}', process.returncode)

    @cli.action('unlock', KeychainArgument.PATH, KeychainArgument.PASSWORD)
    def unlock(self):
        """
        Unlock the specified keychain.
        """
        process, command = self.execute(('security', 'unlock-keychain', '-p', self.password, self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to unlock keychain {self.path}', process.returncode)

    @cli.action('make-default', KeychainArgument.PATH)
    def make_default(self):
        """
        Set the keychain as the system default keychain.
        """
        process, command = self.execute(('security', 'default-keychain', '-s', self.path))
        if process.returncode != 0:
            raise KeychainError(command, f'Unable to set {self.path} as default keychain', process.returncode)

    @cli.action('initialize', KeychainArgument.PATH, KeychainArgument.PASSWORD, KeychainArgument.TIMEOUT)
    def initialize(self, timeout: Optional[Seconds] = None):
        """
        Set up the keychain to be used for code signing. Create the keychain
        at specified path with specified password with given timeout.
        Make it default and unlock it for upcoming use.
        """
        self.create()
        self.set_timeout(timeout=timeout)
        self.make_default()
        self.unlock()
        self.show_info()


if __name__ == '__main__':
    Keychain.invoke_cli()
