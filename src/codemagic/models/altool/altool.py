from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
from contextlib import contextmanager
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import AnyStr
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .altool_result import AltoolResult
from .enums import AuthenticationMethod
from .enums import PlatformType

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect import IssuerId
    from codemagic.apple.app_store_connect import KeyIdentifier
    from codemagic.cli import CliApp


class Altool(RunningCliAppMixin, StringConverterMixin):

    def __init__(self,
                 key_identifier: Optional[KeyIdentifier] = None,
                 issuer_id: Optional[IssuerId] = None,
                 private_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        # JWT authentication fields
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        # Username and password authentication fields
        self._username = username
        self._password = password  # App Specific Password
        self._validate_authentication_info()
        self.logger = log.get_logger(self.__class__)

    @classmethod
    @lru_cache(1)
    def _ensure_altool(cls) -> None:
        try:
            subprocess.check_output(['xcrun', 'altool', '--version'])
        except subprocess.CalledProcessError:
            raise IOError('altool executable is not present on system')

    def _validate_authentication_info(self):
        if self._authentication_method is AuthenticationMethod.NONE:
            raise ValueError(
                'Missing authentication credentials. Either API key and issuer ID '
                'or username and password are required.')
        elif self._authentication_method is AuthenticationMethod.USERNAME_AND_EMAIL:
            is_valid_app_specific_password = bool(re.match(r'^([a-z]{4}-){3}[a-z]{4}$', self._password))
            if not is_valid_app_specific_password:
                raise ValueError(
                    'Invalid App Store Connect password. Expected pattern "abcd-abcd-abcd-abcd". '
                    'Please use app-specific password generated at Apple ID account page. '
                    'See https://support.apple.com/en-us/HT204397 for more information.')

    @property
    def _authentication_method(self) -> AuthenticationMethod:
        if self._username and self._password:
            return AuthenticationMethod.USERNAME_AND_EMAIL
        elif self._key_identifier and self._private_key and self._issuer_id:
            return AuthenticationMethod.JSON_WEB_TOKEN
        else:
            return AuthenticationMethod.NONE

    def _save_api_key_to_disk(self):
        keys_dir = pathlib.Path('~/.private_keys').expanduser()
        keys_dir.mkdir(exist_ok=True)
        key_path = keys_dir / f'AuthKey_{self._key_identifier}.p8'
        key_path.write_text(self._private_key)
        return key_path

    @contextmanager
    def _get_authentication_flags(self):
        private_key_path: Optional[pathlib.Path] = None
        try:
            if self._authentication_method is AuthenticationMethod.JSON_WEB_TOKEN:
                private_key_path = self._save_api_key_to_disk()
                flags = ('--apiKey', self._key_identifier, '--apiIssuer', self._issuer_id)
            elif self._authentication_method is AuthenticationMethod.USERNAME_AND_EMAIL:
                flags = ('--username', self._username, '--password', '@env:APP_STORE_CONNECT_PASSWORD')
                os.environ['APP_STORE_CONNECT_PASSWORD'] = self._password
            else:
                flags = tuple()
            yield flags
        finally:
            if private_key_path:
                private_key_path.unlink()
            try:
                os.environ.pop('APP_STORE_CONNECT_PASSWORD')
            except KeyError:
                pass

    @classmethod
    def _construct_action_command(
            cls, action_name: str, artifact_path: pathlib.Path, auth_flags: Sequence[str]) -> Tuple[str, ...]:
        return (
            'xcrun', 'altool', action_name,
            '--file', str(artifact_path),
            '--type', PlatformType.from_path(artifact_path).value,
            *auth_flags,
            '--output-format', 'json',
        )

    def validate_app(self, artifact_path: pathlib.Path) -> Optional[AltoolResult]:
        self._ensure_altool()
        with self._get_authentication_flags() as auth_flags:
            cmd = self._construct_action_command('--validate-app', artifact_path, auth_flags)
            return self._run_command(cmd, f'Failed to validate archive at "{artifact_path}"')

    def upload_app(self, artifact_path) -> Optional[AltoolResult]:
        self._ensure_altool()
        with self._get_authentication_flags() as auth_flags:
            cmd = self._construct_action_command('--upload-app', artifact_path, auth_flags)
            return self._run_command(cmd, f'Failed to upload archive at "{artifact_path}"')

    def _run_command(self, command: Sequence[str], error_message: str) -> Optional[AltoolResult]:
        process = None
        stdout = ''
        cli_app = self.get_current_cli_app()
        obfuscate_patterns = [self._password] if self._password else []
        try:
            if cli_app:
                process = cli_app.execute(command, obfuscate_patterns, show_output=False)
                stdout = process.stdout
                process.raise_for_returncode()
            else:
                stdout = subprocess.check_output(command, stderr=subprocess.PIPE).decode()
        except subprocess.CalledProcessError as cpe:
            stdout = cpe.stdout
            result = self._get_action_result(cpe.stdout)
            if result and result.product_errors:
                product_errors = '\n'.join(pe.message for pe in result.product_errors)
                error_message = f'{error_message}:\n{product_errors}'
            raise IOError(error_message, process)
        finally:
            self._log_process_output(stdout, cli_app)

        return self._get_action_result(stdout)

    @classmethod
    def _get_action_result(cls, action_stdout: AnyStr) -> Optional[AltoolResult]:
        try:
            parsed_result = json.loads(action_stdout)
            return AltoolResult.create(**parsed_result)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _log_process_output(cls, output: Optional[AnyStr], cli_app: Optional[CliApp]):
        if output is None:
            return

        try:
            result = json.loads(output)
            prettified_result = json.dumps(result, indent=4)
        except ValueError:
            prettified_result = cls._str(output)

        if cli_app:
            cli_app.echo(prettified_result)
        else:
            print(prettified_result)
