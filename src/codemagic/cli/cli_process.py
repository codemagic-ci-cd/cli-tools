#!/usr/bin/env python3

from __future__ import annotations

import shlex
import subprocess
import sys
import threading
import time
import queue
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
        self.stdout = ""
        self.stderr = ""

    @property
    def returncode(self) -> int:
        return self._process.returncode if self._process else 0

    def _log_exec_started(self):
        if self._dry_run:
            self.logger.debug(f'Skip executing "{self.safe_form}" due to dry run')
        else:
            self.logger.debug(f'Execute "{self.safe_form}"')

    def _log_exec_completed(self):
        duration = time.strftime("%M:%S", time.gmtime(self.duration))
        file_logger = log.get_file_logger(self.__class__)
        file_logger.debug('STDOUT: %s', self.stdout)
        file_logger.debug('STDERR: %s', self.stderr)
        self.logger.debug(f'Completed "{self.safe_form}" with returncode {self.returncode} in {duration}')

    def _handle_stream(self, input_stream: IO, output_stream: IO, buffer_size: Optional[int] = None) -> str:
        result: queue.Queue[bytes] = queue.Queue()

        def read_result():
            if buffer_size:
                result.put(input_stream.read(buffer_size))
            else:
                result.put(input_stream.read())

        stream_reader = threading.Thread(target=read_result)
        stream_reader.start()
        stream_reader.join(1)  # Under normal circumstances reading the stream should never take full second

        try:
            chunk = result.get(block=False).decode()
        except queue.Empty:
            chunk = ''

        if self._print_streams:
            output_stream.write(chunk)
        return chunk

    def _handle_streams(self, buffer_size: Optional[int] = None):
        if self._process is None:
            return
        if self._process.stdout:
            self.stdout += self._handle_stream(self._process.stdout, sys.stdout, buffer_size)
        if self._process.stderr:
            self.stderr += self._handle_stream(self._process.stderr, sys.stderr, buffer_size)

    def execute(self,
                stdout: Union[int, IO] = subprocess.PIPE,
                stderr: Union[int, IO] = subprocess.PIPE) -> CliProcess:
        self._log_exec_started()
        start = time.time()
        try:
            if not self._dry_run:
                self._process = subprocess.Popen(self._command_args, stdout=stdout, stderr=stderr)
                while self._process.poll() is None:
                    self._handle_streams(self._buffer_size)
                    time.sleep(0.1)
                self._handle_streams()
        finally:
            self.duration = time.time() - start
            self._log_exec_completed()
        return self

    def raise_for_returncode(self, success_code: int = 0):
        if self.returncode == success_code:
            return
        raise subprocess.CalledProcessError(
            self.returncode, self._command_args, self.stdout, self.stderr)
