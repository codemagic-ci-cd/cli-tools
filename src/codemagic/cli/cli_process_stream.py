from __future__ import annotations

import os
from abc import ABCMeta
from abc import abstractmethod
from typing import IO
from typing import Optional

from codemagic.mixins import StringConverterMixin

if os.name == 'nt':
    import msvcrt

    import _winapi as winapi


class CliProcessStream(StringConverterMixin, metaclass=ABCMeta):

    def __init__(self, input_stream_descriptor: IO, output_stream: IO):
        self._descriptor = input_stream_descriptor
        self._fileno = input_stream_descriptor.fileno()
        self._output_stream = output_stream

    @classmethod
    def create(cls, stream_descriptor: IO, output_stream: IO, blocking: bool = False) -> CliProcessStream:
        if os.name == 'nt':  # Running on Windows
            stream: CliProcessStream = _WindowsCliProcessStream(stream_descriptor, output_stream)
        else:
            stream = _PosixCliProcessStream(stream_descriptor, output_stream)
        if not blocking:
            stream.unblock()
        return stream

    @abstractmethod
    def unblock(self):
        """
        Unblock stream by making the file descriptor async
        """

    @abstractmethod
    def read(self, buffer_size=1024) -> bytes:
        """
        Read up to specified number of bytes from the stream
        """

    @abstractmethod
    def read_all(self) -> bytes:
        """
        Read all remaining bytes from the stream
        """

    def process_buffer(self, buffer_size: Optional[int] = None, multiplex_output: bool = True) -> str:
        if buffer_size:
            bytes_chunk = self.read(buffer_size)
        else:
            bytes_chunk = self.read_all()

        chunk = bytes_chunk.decode(encoding='utf-8', errors='ignore')
        if multiplex_output:
            self._output_stream.write(chunk)
        return chunk


class _PosixCliProcessStream(CliProcessStream):
    def unblock(self):
        os.set_blocking(self._fileno, False)

    def read(self, buffer_size=1024) -> bytes:
        try:
            chunk = self._descriptor.read(buffer_size)
        except IOError:
            # In case we get "Resource temporarily unavailable" from the OS
            chunk = b''
        return self._bytes(chunk or b'')

    def read_all(self) -> bytes:
        return self.read(-1)


class _WindowsCliProcessStream(CliProcessStream):
    PIPE_NOWAIT = 0x00000001

    def __init__(self, stream_descriptor: IO, output_stream: IO):
        super().__init__(stream_descriptor, output_stream)
        self._pipe_handle = msvcrt.get_osfhandle(self._fileno)  # type: ignore

    def unblock(self):
        # https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-setnamedpipehandlestate
        winapi.SetNamedPipeHandleState(self._pipe_handle, self.PIPE_NOWAIT, None, None)

    def read(self, buffer_size=1024) -> bytes:
        # https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile
        try:
            chunk, _result = winapi.ReadFile(self._pipe_handle, buffer_size, 0)  # type: ignore
        except BrokenPipeError:
            chunk = b''
        return self._bytes(chunk or b'')

    def read_all(self) -> bytes:
        # https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-peeknamedpipe
        # Check how much is there still remaining in the pipe to be read and use that as the final buffer size
        try:
            _data, buffer_size, *_rest = winapi.PeekNamedPipe(self._pipe_handle, 1)  # type: ignore
        except BrokenPipeError:
            # The pipe has already been ended
            return b''
        return self.read(buffer_size)
