import io
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import BinaryIO
from typing import Generic
from typing import Iterable
from typing import TextIO
from typing import TypeVar
from typing import Union
from typing import cast

T = TypeVar("T", str, bytes)


class BackwardsIterator(Generic[T], ABC):
    blank_value: T
    line_delimiter: T

    def __init__(self, file_descriptor: Union[TextIO, BinaryIO], buffer_size: int):
        self.file_descriptor = file_descriptor
        self.buffer_size = buffer_size

    @classmethod
    def create(cls, file_descriptor: Union[TextIO, BinaryIO], buffer_size: int):
        if hasattr(file_descriptor, "encoding"):
            return _BackwardsTextIterator(cast(TextIO, file_descriptor), buffer_size)
        return _BackwardsBytesIterator(cast(BinaryIO, file_descriptor), buffer_size)

    @abstractmethod
    def __iter__(self) -> Iterable[str]:
        raise NotImplementedError()

    def _iter_backwards(self) -> Iterable[T]:
        current_segment = None
        offset_from_end = 0
        unprocessed_size = self.file_descriptor.seek(0, io.SEEK_END)
        file_size = unprocessed_size

        while unprocessed_size > 0:
            offset_from_end = min(file_size, offset_from_end + self.buffer_size)
            self.file_descriptor.seek(file_size - offset_from_end)
            buffer = cast(T, self.file_descriptor.read(min(unprocessed_size, self.buffer_size)))
            unprocessed_size -= self.buffer_size
            lines = buffer.splitlines()

            if buffer.endswith(self.line_delimiter):  # Previous segment was not a half line.
                yield current_segment or self.blank_value
            else:  # Previous segment did not end at a line break.
                lines[-1] += current_segment or self.blank_value

            # Retain the first line for next iteration as it might have some portion not captured by current buffer.
            current_segment = lines[0]
            yield from (line for line in reversed(lines[1:]))

        if current_segment is not None:
            yield current_segment


class _BackwardsTextIterator(BackwardsIterator[str]):
    blank_value = ""
    line_delimiter = "\n"

    def __iter__(self) -> Iterable[str]:
        yield from self._iter_backwards()


class _BackwardsBytesIterator(BackwardsIterator[bytes]):
    blank_value = b""
    line_delimiter = b"\n"

    def __iter__(self) -> Iterable[str]:
        yield from (line.decode(errors="ignore") for line in self._iter_backwards())


def iter_backwards(
    file_or_path: Union[TextIO, BinaryIO, Path, str],
    buffer_size=8192,
) -> Iterable[str]:
    """
    A generator that returns the lines of a file in reverse order
    """

    if isinstance(file_or_path, (Path, str)):
        with open(file_or_path, "rb") as fd:
            yield from BackwardsIterator.create(fd, buffer_size)
    else:
        yield from BackwardsIterator.create(file_or_path, buffer_size)
