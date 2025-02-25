import subprocess
from abc import ABCMeta
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.cli import CliProcess
from codemagic.cli import CommandArg
from codemagic.cli.cli_types import ObfuscationPattern
from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin


class ShellTool(
    RunningCliAppMixin,
    StringConverterMixin,
    metaclass=ABCMeta,
):
    def _run_command(
        self,
        command: Sequence[CommandArg],
        *,
        command_env: Optional[Dict[str, str]] = None,
        suppress_output: bool = False,
        show_output: bool = True,
        obfuscate_patterns: Optional[Sequence[ObfuscationPattern]] = None,
    ) -> Union[subprocess.CompletedProcess, CliProcess]:
        if cli_app := self.get_current_cli_app():
            cli_process = cli_app.execute(
                command,
                obfuscate_patterns=obfuscate_patterns,
                env=command_env,
                show_output=show_output,
                suppress_output=suppress_output,
            )
            cli_process.raise_for_returncode()
            return cli_process
        else:
            completed_process = subprocess.run(
                command,
                capture_output=True,
                env=command_env,
            )
            completed_process.check_returncode()
            return completed_process

    @classmethod
    def _get_stdout(cls, completed_process: Union[subprocess.CompletedProcess, CliProcess]) -> str:
        if isinstance(completed_process, subprocess.CompletedProcess):
            return cls._str(completed_process.stdout)
        else:
            return completed_process.stdout

    @classmethod
    def _get_stderr(cls, completed_process: Union[subprocess.CompletedProcess, CliProcess]) -> str:
        if isinstance(completed_process, subprocess.CompletedProcess):
            return cls._str(completed_process.stderr)
        else:
            return completed_process.stderr
