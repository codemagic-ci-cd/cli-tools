import abc
import logging
import pathlib
from typing import Generator


class PathFinderMixin(metaclass=abc.ABCMeta):
    logger: logging.Logger

    def _find_paths(self, pattern: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        if pattern.is_absolute():
            self.logger.info(f'Searching for files matching {pattern}')
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        self.logger.info(f'Searching for files matching {pattern.resolve()}')
        return pathlib.Path().glob(str(pattern))
