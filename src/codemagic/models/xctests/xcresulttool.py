from __future__ import annotations

import json
import pathlib
import subprocess
from tempfile import NamedTemporaryFile
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from codemagic.cli import CommandArg
from codemagic.mixins import RunningCliAppMixin


class XcResultTool(RunningCliAppMixin):

    @classmethod
    def get_bundle(cls, xcresult: pathlib.Path) -> Dict[str, Any]:
        cmd_args: List[CommandArg] = \
            ['xcrun', 'xcresulttool', 'get', '--format', 'json', '--path', xcresult.expanduser()]
        stdout = cls._run_command(cmd_args, f'Failed to get result bundle object from {xcresult}')
        return json.loads(stdout)

    @classmethod
    def get_object(cls, xcresult: pathlib.Path, object_id: str) -> Dict[str, Any]:
        cmd_args: List[CommandArg] = [
            'xcrun', 'xcresulttool', 'get',
            '--format', 'json',
            '--path', xcresult.expanduser(),
            '--id', object_id,
        ]
        stdout = cls._run_command(cmd_args, f'Failed to get result bundle object {object_id} from {xcresult}')
        return json.loads(stdout)

    @classmethod
    def merge(cls, *xcresults: pathlib.Path, result_prefix: Optional[str] = None) -> pathlib.Path:
        assert len(xcresults) > 1, 'At least two xcresults are required for merging'
        with NamedTemporaryFile(prefix=result_prefix or 'Test-', suffix='-merged.xcresult') as tf:
            output_path = pathlib.Path(tf.name)
        cmd_args: List[CommandArg] = ['xcrun', 'xcresulttool', 'merge', *xcresults, '--output-path', output_path]
        _ = cls._run_command(cmd_args, 'Failed to merge xcresult bundles')
        return output_path

    @classmethod
    def _run_command(cls, command_args: Sequence[CommandArg], error_message: str) -> str:
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(command_args, suppress_output=True)
                process.raise_for_returncode()
                return process.stdout
            else:
                return subprocess.check_output(command_args).decode()
        except subprocess.CalledProcessError:
            raise IOError(error_message)
