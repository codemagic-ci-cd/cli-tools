#!/usr/bin/env python3

from __future__ import annotations

import logging
import subprocess
import sys
import time
from typing import Optional, Sequence, IO

from .cli_types import CommandArg, ObfuscatedCommand


class CliProcess:

    def __init__(self, command_args: Sequence[CommandArg],
                 safe_form: ObfuscatedCommand,
                 print_streams: bool = True,
                 dry: bool = False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.duration: float = 0
        self._process: Optional[subprocess.Popen] = None
        self._command_args = command_args
        self._dry_run = dry
        self._print_streams = print_streams
        self._buffer_size = 8192
        self.safe_form = safe_form
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
        self.logger.debug(f'Completed "{self.safe_form}" with returncode {self.returncode} in {self.duration:.2f}')

    def _handle_stream(self, input_stream: IO, output_stream: IO, buffer_size: Optional[int] = None):
        chunk = (input_stream.read(buffer_size) if buffer_size else input_stream.read()).decode()
        if self._print_streams:
            output_stream.write(chunk)
        return chunk

    def _handle_streams(self, buffer_size: Optional[int] = None):
        if self._process is None:
            return
        self.stdout += self._handle_stream(self._process.stdout, sys.stdout, buffer_size)
        self.stderr += self._handle_stream(self._process.stderr, sys.stderr, buffer_size)

    def execute(self) -> CliProcess:
        self._log_exec_started()
        start = time.time()
        try:
            if not self._dry_run:
                self._process = subprocess.Popen(self._command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while self._process.poll() is None:
                    self._handle_streams(self._buffer_size)
                    time.sleep(0.1)
                self._handle_streams()
        finally:
            self.duration = time.time() - start
            self._log_exec_completed()
        return self
