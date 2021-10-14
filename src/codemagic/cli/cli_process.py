#!/usr/bin/env python3

from __future__ import annotations

import shlex
import subprocess
import sys
import time
from typing import IO
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.utilities import log

from .cli_process_stream import CliProcessStream
from .cli_types import CommandArg
from .cli_types import ObfuscatedCommand


class CliProcess:

    def __init__(self, command_args: Sequence[CommandArg],
                 safe_form: Optional[ObfuscatedCommand] = None,
                 print_streams: bool = True,
                 dry: bool = False):
        self.logger = log.get_logger(self.__class__)
        self.duration: float = 0
        self._process: Optional[subprocess.Popen] = None
        self._command_args = command_args
        self._dry_run = dry
        self._print_streams = print_streams
        self._buffer_size = 8192
        self.safe_form = safe_form
        if safe_form is None:
            full_command = ' '.join(shlex.quote(str(arg)) for arg in command_args)
            self.safe_form = ObfuscatedCommand(full_command)
        self._stdout = ''
        self._stderr = ''
        self._stdout_stream: Optional[CliProcessStream] = None
        self._stderr_stream: Optional[CliProcessStream] = None

    @property
    def stdout(self) -> str:
        return self._stdout

    @property
    def stderr(self) -> str:
        return self._stderr

    @property
    def returncode(self) -> int:
        return self._process.returncode if self._process else 0

    def _log_exec_started(self):
        if self._dry_run:
            self.logger.debug(f'Skip executing "{self.safe_form}" due to dry run')
        else:
            self.logger.debug(f'Execute "{self.safe_form}"')

    def _log_exec_completed(self):
        duration = time.strftime('%M:%S', time.gmtime(self.duration))
        file_logger = log.get_file_logger(self.__class__)
        file_logger.debug('STDOUT: %s', self.stdout)
        file_logger.debug('STDERR: %s', self.stderr)
        self.logger.debug(f'Completed "{self.safe_form}" with returncode {self.returncode} in {duration}')

    def _handle_streams(self, buffer_size: Optional[int] = None):
        if self._process is None:
            return
        if self._stdout_stream:
            self._stdout += self._stdout_stream.process_buffer(buffer_size, self._print_streams)
        if self._stderr_stream:
            self._stderr += self._stderr_stream.process_buffer(buffer_size, self._print_streams)

    def _configure_process_streams(self):
        if self._process.stdout:
            self._stdout_stream = CliProcessStream.create(self._process.stdout, sys.stdout, blocking=False)
        if self._process.stderr:
            self._stderr_stream = CliProcessStream.create(self._process.stderr, sys.stderr, blocking=False)

    def execute(self,
                stdout: Union[int, IO] = subprocess.PIPE,
                stderr: Union[int, IO] = subprocess.PIPE) -> CliProcess:
        self._log_exec_started()
        start = time.time()
        try:
            if not self._dry_run:
                self._process = subprocess.Popen(self._command_args, stdout=stdout, stderr=stderr)
                self._configure_process_streams()
                while self._process.poll() is None:
                    self._handle_streams(self._buffer_size)
                    time.sleep(0.1)
                self._handle_streams()
        finally:
            self.duration = time.time() - start
            self._log_exec_completed()
        return self

    def raise_for_returncode(self, success_code: int = 0, include_logs: bool = True):
        if self.returncode == success_code:
            return
        if include_logs:
            stdout = self.stdout
            stderr = self.stderr
        else:
            stdout = ''
            stderr = ''
        raise subprocess.CalledProcessError(self.returncode, self._command_args, stdout, stderr)
