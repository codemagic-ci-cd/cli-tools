import io
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import TextIO
from typing import Union


def _iter_backwards(file_descriptor: TextIO, buffer_size: int, file_size: Optional[int] = None):
    current_segment = None
    offset_from_end = 0
    unprocessed_size = file_descriptor.seek(0, io.SEEK_END)
    if file_size is None:
        file_size = unprocessed_size

    while unprocessed_size > 0:
        offset_from_end = min(file_size, offset_from_end + buffer_size)
        file_descriptor.seek(file_size - offset_from_end)
        buffer = file_descriptor.read(min(unprocessed_size, buffer_size))
        unprocessed_size -= buffer_size
        lines = buffer.splitlines()

        if buffer.endswith('\n'):  # Previous segment was not a half line.
            yield current_segment or ''
        else:  # Previous segment did not end at a line break.
            lines[-1] += current_segment or ''

        # Retain the first line for next iteration as it might have some
        # portion not captured by current buffer.
        current_segment = lines[0]
        for line in reversed(lines[1:]):
            yield line

    if current_segment is not None:
        yield current_segment


def iter_backwards(
    file_or_path: Union[TextIO, Path, str],
    buffer_size=8192,
) -> Iterable[str]:
    """
    A generator that returns the lines of a file in reverse order
    """

    if isinstance(file_or_path, (Path, str)):
        file_path = Path(file_or_path)
        with file_path.open() as fd:
            yield from _iter_backwards(fd, buffer_size, file_size=file_path.stat().st_size)
    else:
        yield from _iter_backwards(file_or_path, buffer_size)
