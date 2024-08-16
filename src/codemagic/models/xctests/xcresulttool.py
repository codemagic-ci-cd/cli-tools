from __future__ import annotations

import json
import pathlib
import re
import subprocess
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from packaging.version import Version

from codemagic.cli import CommandArg
from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class XcResultToolError(IOError):
    def __init__(self, message: str, stderr: str):
        super().__init__(message)
        self.stderr = stderr


class XcResultTool(RunningCliAppMixin, StringConverterMixin):
    @classmethod
    @lru_cache(1)
    def get_tool_version(cls) -> Optional[Version]:
        # Cache xcresulttool version to avoid repeated checks.
        # Assumes Xcode (and thus xcresulttool) version remains constant during execution.

        cmd_args = ["xcrun", "xcresulttool", "version"]
        try:
            stdout = cls._run_command(cmd_args, "Failed to obtain xcresulttool version")
        except XcResultToolError as e:
            log.get_file_logger(cls).exception(str(e))
            return None

        version_output = cls._str(stdout.strip())
        # Expected version output of xcresulttool (bundled with Xcode 16.0 beta 3) is as follows:
        # xcresulttool version 23024, format version 3.53 (current)
        match = re.match(r"^xcresulttool version (?P<version>\d+(\.\d+)?)", version_output)

        if not match:
            log.get_file_logger(cls).error("Failed to capture xcresulttool version from %r", version_output)
            return None

        return Version(match.group("version"))

    @classmethod
    def _requires_legacy_flag(cls) -> bool:
        """
        Starting from Xcode 16 beta 3 'xcresulttool get --format json' has been deprecated and
        cannot be used without '--legacy' flag.
        """

        version = cls.get_tool_version()
        if not version:
            return False
        return version >= Version("23021")

    @classmethod
    def get_bundle(cls, xcresult: pathlib.Path) -> Dict[str, Any]:
        cmd_args: List[CommandArg] = [
            "xcrun",
            "xcresulttool",
            "get",
            "--format",
            "json",
            "--path",
            xcresult.expanduser(),
        ]

        if cls._requires_legacy_flag():
            cmd_args.append("--legacy")

        stdout = cls._run_command(cmd_args, f"Failed to get result bundle object from {xcresult}")
        return json.loads(stdout)

    @classmethod
    def get_object(cls, xcresult: pathlib.Path, object_id: str) -> Dict[str, Any]:
        cmd_args: List[CommandArg] = [
            "xcrun",
            "xcresulttool",
            "get",
            "--format",
            "json",
            "--path",
            xcresult.expanduser(),
            "--id",
            object_id,
        ]

        if cls._requires_legacy_flag():
            cmd_args.append("--legacy")

        stdout = cls._run_command(cmd_args, f"Failed to get result bundle object {object_id} from {xcresult}")
        return json.loads(stdout)

    @classmethod
    def merge(cls, *xcresults: pathlib.Path, result_prefix: Optional[str] = None) -> pathlib.Path:
        assert len(xcresults) > 1, "At least two xcresults are required for merging"
        with NamedTemporaryFile(prefix=result_prefix or "Test-", suffix="-merged.xcresult") as tf:
            output_path = pathlib.Path(tf.name)
        cmd_args: List[CommandArg] = ["xcrun", "xcresulttool", "merge", *xcresults, "--output-path", output_path]
        _ = cls._run_command(cmd_args, "Failed to merge xcresult bundles")
        return output_path

    @classmethod
    def _run_command(cls, command_args: Sequence[CommandArg], error_message: str) -> bytes:
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                return cls._run_command_with_cli_app(cli_app, command_args)
            else:
                return subprocess.check_output(command_args)
        except subprocess.CalledProcessError as cpe:
            raise XcResultToolError(error_message, cls._str(cpe.stderr)) from cpe

    @classmethod
    def _run_command_with_cli_app(cls, cli_app: CliApp, command_args: Sequence[CommandArg]) -> bytes:
        """
        Replace default stdout stream with direct file handle to bypass stream
        processing in Python which can be very slow. For example
        `xcrun xcresulttool get --format json --path results.xcresult --id 'object-id'`
        can output 500K+ lines at 30+ MB. Processing it in small chunks in Python is very
        time-consuming whereas using file handles is almost instantaneous.
        """
        with NamedTemporaryFile(mode="w+b") as stdout_fd:
            process = cli_app.execute(command_args, suppress_output=True, stdout=stdout_fd)
            process.raise_for_returncode()
            stdout_fd.flush()
            stdout_fd.seek(0)
            return stdout_fd.read()
