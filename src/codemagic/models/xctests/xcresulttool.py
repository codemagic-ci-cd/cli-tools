from __future__ import annotations

import json
import pathlib
import subprocess
from collections import Sequence
from typing import Optional
from typing import Union

from codemagic.mixins import RunningCliAppMixin


class XcResultTool(RunningCliAppMixin):

    @classmethod
    def get(cls, xcresult: pathlib.Path, object_id: Optional[str] = None):
        id_args = ['--id', object_id] if object_id else []
        # cmd_args = ['xcrun', 'xcresulttool', 'get', '--format', 'json', '--path', xcresult]
        # stdout = cls._run_command(cmd_args)
        # return json.loads(stdout)

    @classmethod
    def merge(cls, *xcresults: pathlib.Path) -> pathlib.Path:
        # TODO
        output_path = pathlib.Path()
        # cmd_args = ['xcrun', 'xcresulttool', 'merge', *xcresults, '--output-path', output_path]
        # _ = cls._run_command(cmd_args)
        return output_path

    @classmethod
    def _run_command(cls, command_args: Sequence[Union[str, pathlib.Path]]) -> str:
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(command_args, suppress_output=True)
                process.raise_for_returncode()
                return process.stdout
            else:
                return subprocess.check_output(command_args).decode()
        except subprocess.CalledProcessError:
            raise IOError('Failed to list available test devices')
