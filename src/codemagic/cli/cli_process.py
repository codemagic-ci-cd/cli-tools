#!/usr/bin/env python3

from __future__ import annotations

import fcntl
import os
import shlex
import subprocess
import sys
import time
from typing import IO
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.utilities import log

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

    def _ensure_process_streams_are_non_blocking(self):
        for stream in (self._process.stdout, self._process.stderr):
            if stream is None:
                continue
            stream_descriptor = stream.fileno()
            current_stream_flags = fcntl.fcntl(stream_descriptor, fcntl.F_GETFL)
            fcntl.fcntl(stream_descriptor, fcntl.F_SETFL, current_stream_flags | os.O_NONBLOCK)

    def _handle_stream(self, input_stream: IO, output_stream: IO, buffer_size: Optional[int] = None) -> str:
        if buffer_size:
            bytes_chunk = input_stream.read(buffer_size)
        else:
            bytes_chunk = input_stream.read()

        chunk = '' if bytes_chunk is None else bytes_chunk.decode()
        if self._print_streams:
            output_stream.write(chunk)
        return chunk

    def _handle_streams(self, buffer_size: Optional[int] = None):
        if self._process is None:
            return
        if self._process.stdout:
            self._stdout += self._handle_stream(self._process.stdout, sys.stdout, buffer_size)
        if self._process.stderr:
            self._stderr += self._handle_stream(self._process.stderr, sys.stderr, buffer_size)

    def execute(self,
                stdout: Union[int, IO] = subprocess.PIPE,
                stderr: Union[int, IO] = subprocess.PIPE) -> CliProcess:
        self._log_exec_started()
        start = time.time()
        try:
            if not self._dry_run:
                self._process = subprocess.Popen(self._command_args, stdout=stdout, stderr=stderr)
                self._ensure_process_streams_are_non_blocking()
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
