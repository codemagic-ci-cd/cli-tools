from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import AnyStr
from typing import Callable
from typing import Generator
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

import psutil

from codemagic.cli import CliProcess
from codemagic.cli import CliProcessHealthCheckError
from codemagic.cli import environment
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


StrTuple = Union[Tuple[()], Tuple[str, ...]]  # Empty or variable length tuple with str elements


class AltoolCommandError(Exception):
    def __init__(self, error_message: str, process_output: str):
        super().__init__(error_message)
        self.process_output = process_output


class CFNetworkingRetryError(AltoolCommandError):
    pass


class Altool(RunningCliAppMixin, StringConverterMixin):
    def __init__(
        self,
        key_identifier: Optional[KeyIdentifier] = None,
        issuer_id: Optional[IssuerId] = None,
        private_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verbose: bool = False,
    ):
        # JWT authentication fields
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        # Username and password authentication fields
        self._username = username
        self._password = password  # App Specific Password
        self._validate_authentication_info()
        self.logger = log.get_logger(self.__class__)
        self.verbose = verbose

    @classmethod
    @lru_cache(1)
    def _ensure_altool(cls) -> None:
        try:
            subprocess.check_output(["xcrun", "altool", "--version"])
        except subprocess.CalledProcessError:
            raise IOError("altool executable is not present on system")

    def _validate_authentication_info(self):
        if self._authentication_method is AuthenticationMethod.NONE:
            raise ValueError(
                "Missing authentication credentials. Either API key and issuer ID "
                "or username and password are required.",
            )
        elif self._authentication_method is AuthenticationMethod.USERNAME_AND_EMAIL:
            is_valid_app_specific_password = bool(re.match(r"^([a-z]{4}-){3}[a-z]{4}$", self._password))
            if not is_valid_app_specific_password:
                raise ValueError(
                    'Invalid App Store Connect password. Expected pattern "abcd-abcd-abcd-abcd". '
                    "Please use app-specific password generated at Apple ID account page. "
                    "See https://support.apple.com/en-us/HT204397 for more information.",
                )

    @property
    def _authentication_method(self) -> AuthenticationMethod:
        if self._username and self._password:
            return AuthenticationMethod.USERNAME_AND_EMAIL
        elif self._key_identifier and self._private_key and self._issuer_id:
            return AuthenticationMethod.JSON_WEB_TOKEN
        else:
            return AuthenticationMethod.NONE

    def _save_api_key_to_disk(self):
        keys_dir = pathlib.Path("~/.private_keys").expanduser()
        keys_dir.mkdir(exist_ok=True)
        key_path = keys_dir / f"AuthKey_{self._key_identifier}.p8"
        key_path.write_text(self._private_key)
        return key_path

    @contextmanager
    def _get_authentication_flags(self) -> Generator[StrTuple, None, None]:
        private_key_path: Optional[pathlib.Path] = None
        try:
            if self._authentication_method is AuthenticationMethod.JSON_WEB_TOKEN:
                assert self._key_identifier is not None  # Make mypy happy
                assert self._issuer_id is not None  # Make mypy happy
                private_key_path = self._save_api_key_to_disk()
                flags: StrTuple = ("--apiKey", str(self._key_identifier), "--apiIssuer", str(self._issuer_id))
            elif self._authentication_method is AuthenticationMethod.USERNAME_AND_EMAIL:
                assert isinstance(self._username, str)  # Make mypy happy
                assert isinstance(self._password, str)  # Make mypy happy
                flags = ("--username", self._username, "--password", "@env:APP_STORE_CONNECT_PASSWORD")
                os.environ["APP_STORE_CONNECT_PASSWORD"] = self._password
            else:
                flags = tuple()
            yield flags
        finally:
            if private_key_path:
                private_key_path.unlink()
            try:
                os.environ.pop("APP_STORE_CONNECT_PASSWORD")
            except KeyError:
                pass

    def _construct_action_command(
        self,
        action_name: str,
        artifact_path: pathlib.Path,
        auth_flags: Sequence[str],
    ) -> Tuple[str, ...]:
        verbose_flags = ["--verbose"] if self.verbose else []
        return (
            "xcrun",
            "altool",
            action_name,
            "--file",
            str(artifact_path),
            "--type",
            PlatformType.from_path(artifact_path).value,
            *auth_flags,
            "--output-format",
            "json",
            *verbose_flags,
        )

    def validate_app(
        self,
        artifact_path: pathlib.Path,
        retries: int = 1,
        retry_wait_seconds: Union[int, float] = 0.5,
    ) -> Optional[AltoolResult]:
        self._ensure_altool()
        with self._get_authentication_flags() as auth_flags:
            cmd = self._construct_action_command("--validate-app", artifact_path, auth_flags)
            return self._run_retrying_command(cmd, artifact_path, "validate", retries, retry_wait_seconds)

    def upload_app(
        self,
        artifact_path: pathlib.Path,
        retries: int = 1,
        retry_wait_seconds: Union[int, float] = 0.5,
    ) -> Optional[AltoolResult]:
        self._ensure_altool()
        with self._get_authentication_flags() as auth_flags:
            cmd = self._construct_action_command("--upload-app", artifact_path, auth_flags)
            return self._run_retrying_command(cmd, artifact_path, "upload", retries, retry_wait_seconds)

    def _run_retrying_command(
        self,
        command: Sequence[str],
        artifact_path: pathlib.Path,
        action_name: str,
        retries: int,
        retry_delay: Union[int, float],
    ) -> Optional[AltoolResult]:
        cli_app = self.get_current_cli_app()
        initial_retry_count = retries
        attempt = 0

        if cli_app:
            print_fn: Callable[[str], None] = cli_app.echo
        else:
            print_fn = print

        while attempt == 0 or retries > 0:
            retries -= 1
            attempt += 1
            try:
                return self._run_command(command, f'Failed to {action_name} archive at "{artifact_path}"', cli_app)
            except AltoolCommandError as error:
                has_retries = retries > 0
                should_retry = self._should_retry_command(error)
                if has_retries and should_retry:
                    if attempt == 1:
                        print_fn(f"Failed to {action_name} archive, but this might be a temporary issue, retrying...")
                    else:
                        print_fn(f"Attempt #{attempt} to {action_name} failed, retrying...")
                    self._kill_xcode_processes_for_retrying()
                else:
                    if initial_retry_count > retries + 1:  # Only print this in case retrying was used
                        print_fn(f"Attempt #{attempt} to {action_name} failed.")
                    self._log_process_output(error.process_output, cli_app)
                    raise IOError(str(error)) from error

            self.logger.debug(f"Wait {retry_delay:.1f}s after failed attempt #{attempt}, {retries} tries remaining")
            time.sleep(retry_delay)
        raise RuntimeError("Did not return")

    def _kill_xcode_processes_for_retrying(self):
        if not environment.is_ci_environment():
            return  # Skip killing Xcodes if not running in CI environment

        for process in psutil.process_iter():
            try:
                process_name = process.name()
                if "xcode" not in process_name.lower():
                    continue
                process.kill()
            except psutil.Error as error:
                self.logger.debug("Failed to kill Xcode process: %s", error)
            else:
                self.logger.debug("Killed Xcode process (pid=%d, name=%s)", process.pid, process_name)

    def _run_command(
        self,
        command: Sequence[str],
        error_message: str,
        cli_app: Optional[CliApp],
    ) -> Optional[AltoolResult]:
        obfuscate_patterns = [self._password] if self._password else []
        process = None
        try:
            if cli_app:
                logs_inspector = CFNetworkErrorLogsInspector("altool", datetime.now())
                process = CliProcess(
                    command,
                    cli_app.obfuscate_command(command, obfuscate_patterns),
                    print_streams=cli_app.verbose,
                    # Less than 100 should be fine. Retry attempts get to thousands within minutes
                    process_health_check=lambda _: logs_inspector.get_estimated_errors_count() < 100,
                    process_health_check_interval=10,
                )
                process.execute(stderr=subprocess.STDOUT)
                stdout = process.stdout
                process.raise_for_returncode()
            else:
                stdout = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        except CliProcessHealthCheckError as hce:
            raise CFNetworkingRetryError(
                f"{error_message}: Connection to Apple's cloud storage failed",
                process.stdout if process else "",
            ) from hce
        except subprocess.CalledProcessError as cpe:
            result = self._get_action_result(cpe.stdout)
            if result and result.product_errors:
                product_errors = "\n".join(pe.message for pe in result.product_errors)
                error_message = f"{error_message}:\n{product_errors}"
            raise AltoolCommandError(
                error_message,
                self._hide_environment_variable_values(cpe.stdout),
            )

        self._log_process_output(stdout, cli_app)
        return self._get_action_result(stdout)

    @classmethod
    def _hide_environment_variable_values(cls, altool_output: Optional[AnyStr]) -> str:
        """
        With certain Xcode versions all defined environment variables
        are printed out by ipatool as Ruby mapping in case an error occurs.
        Since environment variables can contain all kinds of secrets
        it is not desirable to have them in the publishing output.
        """
        if altool_output is None:
            return ""

        output = cls._str(altool_output)
        env_match = re.search(r"ENV: \{(.*)\}", output)

        if env_match is not None:
            # Ruby hashes are represented as `{ "name" => "value", "key" => "other value", ... }
            # This pattern captures the variable name before `=>`.
            environment_variable_names = re.findall(r',?"([^"]+)"\s?=>', env_match.group(1))
            sanitized_environment = ", ".join(f'"{name}"=>"..."' for name in environment_variable_names)
            output = f"{output[:env_match.span()[0]]}ENV: {{{sanitized_environment}}}{output[env_match.span()[1]:]}"

        return output

    @classmethod
    def _should_retry_command(cls, error: Union[AltoolCommandError, CFNetworkingRetryError]):
        if isinstance(error, CFNetworkingRetryError):
            return True

        patterns = (
            re.compile("Unable to authenticate.*-19209"),
            re.compile("server returned an invalid response.*try your request again"),
            re.compile("The request timed out."),
        )
        process_output = cast(AltoolCommandError, error).process_output
        return any(pattern.search(process_output) for pattern in patterns)

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
            prettified_result = cls._hide_environment_variable_values(output)

        if cli_app:
            cli_app.echo(prettified_result)
        else:
            print(prettified_result)


class CFNetworkErrorLogsInspector:
    ERROR_PATTERN = re.compile(r"^Task <[\w-]+>\.<(\d+)> finished with error")

    def __init__(self, process: str, start: datetime):
        self.logger = log.get_file_logger(self.__class__)
        predicate = " and ".join(
            [
                'subsystem=="com.apple.CFNetwork"',
                f'process=="{process}"',
                'eventMessage contains "finished with error"',
                'eventMessage contains "Error Domain=NSURLErrorDomain"',
                'eventMessage contains "Code=-1003"',
            ],
        )
        self.logs_command = (
            "log",
            "show",
            "--no-backtrace",
            "--no-debug",
            "--no-info",
            "--no-pager",
            *("--start", start.strftime("%Y-%m-%d %H:%M:%S")),
            *("--predicate", predicate),
            *("--style", "ndjson"),
        )

    def iter_log_entries(self):
        start = time.time()
        try:
            cp = subprocess.run(
                self.logs_command,
                capture_output=True,
                check=True,
                timeout=10,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            self.logger.exception("Checking CFNetwork error logs failed")
            return
        finally:
            self.logger.debug(f"Completed CFNetwork error logs check in {time.time() - start:.2f}s")

        for line in cp.stdout.splitlines():
            try:
                log_entry = json.loads(line)
                if log_entry.get("eventMessage") is not None:
                    yield log_entry
            except ValueError:
                pass

    def get_estimated_errors_count(self) -> int:
        count = sum(1 for log_entry in self.iter_log_entries() if self.ERROR_PATTERN.match(log_entry["eventMessage"]))
        self.logger.debug(f"Found {count} log that hint indefinite CFNetwork retry loop")
        return count
