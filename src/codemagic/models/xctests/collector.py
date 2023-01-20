from __future__ import annotations

import pathlib
import shutil
from itertools import takewhile
from typing import List
from typing import Optional
from typing import Set

from codemagic.utilities import log

from .xcresulttool import XcResultTool


class XcResultCollector:

    def __init__(self) -> None:
        self.logger = log.get_logger(self.__class__)
        self._ignore_xcresults: Set[pathlib.Path] = set()
        self._gathered_xcresults: Set[pathlib.Path] = set()
        self._xcresult: Optional[pathlib.Path] = None
        self._xcresult_is_merged = False

    def forget_merged_result(self):
        if self._xcresult and self._xcresult_is_merged:
            self.logger.debug('Remove merged xcresult at %s', self._xcresult)
            shutil.rmtree(self._xcresult)
            self._xcresult = None
            self._xcresult_is_merged = False
        else:
            # Do not remove non-merged results
            pass

    @classmethod
    def _find_results(cls, tests_directory: pathlib.Path) -> Set[pathlib.Path]:
        tests_directory = tests_directory.expanduser()
        if not tests_directory.is_dir():
            return set()  # Not a directory, cannot gather results
        elif tests_directory.suffix == '.xcresult':
            return {tests_directory}
        else:
            return set(tests_directory.rglob('*.xcresult'))

    def ignore_results(self, tests_directory: pathlib.Path) -> XcResultCollector:
        xcresults = self._find_results(tests_directory)
        self._ignore_xcresults.update(xcresults)
        return self

    def gather_results(self, tests_directory: pathlib.Path) -> XcResultCollector:
        xcresults = self._find_results(tests_directory)
        self._gathered_xcresults.update(xcresults)
        self.forget_merged_result()
        return self

    def get_merged_xcresult(self) -> pathlib.Path:
        if self._xcresult:
            return self._xcresult

        xcresults = self.get_collected_results()
        if not xcresults:
            raise ValueError('No test results were found')
        elif len(xcresults) == 1:
            self._xcresult = xcresults[0]
            self._xcresult_is_merged = False
        else:
            self._xcresult = XcResultTool.merge(
                *self._gathered_xcresults,
                result_prefix=self._get_merged_result_prefix(),
            )
            self._xcresult_is_merged = True
        return self._xcresult

    def get_collected_results(self) -> List[pathlib.Path]:
        return sorted([p for p in self._gathered_xcresults if p not in self._ignore_xcresults])

    def _get_merged_result_prefix(self) -> str:
        assert len(self._gathered_xcresults) > 1
        matching_chars = takewhile(lambda cs: len(set(cs)) == 1, zip(*(p.stem for p in self._gathered_xcresults)))
        return ''.join(chars[0] for chars in matching_chars)
