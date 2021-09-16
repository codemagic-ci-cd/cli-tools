import io
from pathlib import Path
from typing import Iterable
from typing import Union


class BackwardsFileReader:

    def __init__(self, file_path: Union[Path, str], buffer_size=8192):
        self._file_path = Path(file_path)
        self._size = self._file_path.stat().st_size
        self._buffer_size = buffer_size

    def iter_backwards(self) -> Iterable[str]:
        """A generator that returns the lines of a file in reverse order"""
        with open(self._file_path) as fd:
            current_segment = None
            offset_from_end = 0
            unprocessed_size = fd.seek(0, io.SEEK_END)

            while unprocessed_size > 0:
                offset_from_end = min(self._size, offset_from_end + self._buffer_size)
                fd.seek(self._size - offset_from_end)
                buffer = fd.read(min(unprocessed_size, self._buffer_size))
                unprocessed_size -= self._buffer_size
                lines = buffer.splitlines()

                if buffer.endswith('\n'):  # Previous segment was not a half line.
                    yield current_segment or ''
                else:  # Previous segment did not end at a line break.
                    lines[-1] += current_segment or ''

                # Retain the first line for next iteration as it might might have some
                # portion not captured by current buffer.
                current_segment = lines[0]
                for line in reversed(lines[1:]):
                    yield line

            if current_segment is not None:
                yield current_segment
