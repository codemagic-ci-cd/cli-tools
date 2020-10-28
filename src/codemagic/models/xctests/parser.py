from __future__ import annotations

import pathlib
from typing import List
from typing import Optional
from typing import Set

from codemagic.models.junit import TestSuite
from codemagic.utilities import log
from .xcresult import ActionTestPlanRunSummaries
from .xcresult import ActionTestPlanRunSummary
from .xcresult import ActionTestableSummary
from .xcresult import ActionsInvocationRecord
from .xcresulttool import XcResultTool

DEFAULT_DERIVED_DATA_PATH = pathlib.Path('~/Library/Developer/Xcode/DerivedData/').expanduser()


class XcResultParser:

    def __init__(self):
        self.logger = log.get_logger(self.__class__)
        self._xcresults: Set[pathlib.Path] = set()
        self._xcresult: Optional[pathlib.Path] = None

    def gather_results(self, tests_directory: pathlib.Path = DEFAULT_DERIVED_DATA_PATH) -> XcResultParser:
        assert tests_directory.is_dir(), 'Not a directory, cannot gather results'
        tests_directory = tests_directory.expanduser()

        if tests_directory.suffix == '.xcresult':
            self._xcresults.add(tests_directory)
        else:
            self._xcresults.update(tests_directory.rglob('*.xcresult'))
        return self

    def _choose_xcresult(self) -> pathlib.Path:
        if self._xcresult:
            return self._xcresult

        if not self._xcresults:
            raise ValueError('No test results were found')
        elif len(self._xcresults) == 1:
            self._xcresult = next(iter(self._xcresults))
        else:
            self._xcresult = XcResultTool.merge(*self._xcresults)
        return self._xcresult

    def _testable_summary_to_test_suite(self, testable_summary: ActionTestableSummary) -> TestSuite:
        test_suite = TestSuite(
            name=testable_summary.name or '',
            tests=len(testable_summary.tests)
        )
        return test_suite

    def _get_test_suites(self, invocation_record: ActionsInvocationRecord) -> List[TestSuite]:
        summaries: List[Optional[ActionTestPlanRunSummaries]] = \
            [action.action_result.get_action_test_plan_run_summaries() for action in invocation_record.actions]
        all_summaries: List[List[ActionTestPlanRunSummary]] = \
            [run_summaries.summaries for run_summaries in summaries if run_summaries]
        test_summaries: List[ActionTestPlanRunSummary] = \
            [summary for _summaries in all_summaries for summary in _summaries]
        testable_summaries: List[ActionTestableSummary] = \
            [testable_summary for test_summary in test_summaries for testable_summary in
             test_summary.testable_summaries]
        return [self._testable_summary_to_test_suite(ts) for ts in testable_summaries]

    def parse_results(self) -> List[TestSuite]:
        xcresult = self._choose_xcresult()
        invocation_record = ActionsInvocationRecord.from_xcresult(xcresult)
        testsuite_metadata = invocation_record.get_metadata()
        test_suites = self._get_test_suites(invocation_record)
        return test_suites
