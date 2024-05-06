from __future__ import annotations

import abc
import logging
import pathlib
from typing import Iterator


class PathFinderMixin(metaclass=abc.ABCMeta):
    logger: logging.Logger

    def glob(self, pattern: pathlib.Path) -> Iterator[pathlib.Path]:
        if pattern.is_absolute():
            self.logger.info(f"Searching for files matching {pattern}")
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        elif pattern == pathlib.Path("."):
            self.logger.info(f"Searching for files matching {pattern.resolve()}")
            # `Path('.').glob('.')` which this would essentially cause is erroneous.
            # Return empty iterator as we cannot possibly find current directory from
            # within the same directory.
            return iter([])
        else:
            self.logger.info(f"Searching for files matching {pattern.resolve()}")
            return pathlib.Path().glob(str(pattern))

    def find_paths(self, *patterns: pathlib.Path) -> Iterator[pathlib.Path]:
        for pattern in patterns:
            yield from self.glob(pattern.expanduser())
