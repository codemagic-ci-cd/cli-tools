from __future__ import annotations

import pathlib
from typing import Optional
from typing import Set

from codemagic.utilities import log
from .xcresulttool import XcResultTool

DEFAULT_DERIVED_DATA_PATH = pathlib.Path('~/Library/Developer/Xcode/DerivedData/').expanduser()


class XcResultCollector:

    def __init__(self):
        self.logger = log.get_logger(self.__class__)
        self._xcresults: Set[pathlib.Path] = set()
        self._xcresult: Optional[pathlib.Path] = None

    def gather_results(self, tests_directory: pathlib.Path = DEFAULT_DERIVED_DATA_PATH) -> XcResultCollector:
        assert tests_directory.is_dir(), 'Not a directory, cannot gather results'
        tests_directory = tests_directory.expanduser()

        if tests_directory.suffix == '.xcresult':
            self._xcresults.add(tests_directory)
        else:
            self._xcresults.update(tests_directory.rglob('*.xcresult'))
        return self

    def choose_xcresult(self) -> pathlib.Path:
        if self._xcresult:
            return self._xcresult

        if not self._xcresults:
            raise ValueError('No test results were found')
        elif len(self._xcresults) == 1:
            self._xcresult = next(iter(self._xcresults))
        else:
            self._xcresult = XcResultTool.merge(*self._xcresults)
        return self._xcresult
