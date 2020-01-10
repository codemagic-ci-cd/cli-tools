import abc
import logging
import pathlib
from typing import Generator


class PathFinderMixin(metaclass=abc.ABCMeta):
    logger: logging.Logger

    def glob(self, pattern: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        if pattern.is_absolute():
            self.logger.info(f'Searching for files matching {pattern}')
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        self.logger.info(f'Searching for files matching {pattern.resolve()}')
        return pathlib.Path().glob(str(pattern))

    def find_paths(self, *patterns: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        for pattern in patterns:
            for path in self.glob(pattern.expanduser()):
                yield path
