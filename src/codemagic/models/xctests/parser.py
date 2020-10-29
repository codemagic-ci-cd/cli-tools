from __future__ import annotations

import pathlib
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set

from codemagic.models.junit import Error
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuite
from codemagic.models.junit import TestSuites
from codemagic.utilities import log
from .xcresult import ActionRecord
from .xcresult import ActionRunDestinationRecord
from .xcresult import ActionTestMetadata
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

    @classmethod
    def _get_test_case(cls, test: ActionTestMetadata) -> TestCase:
        testcase = TestCase(
            name=test.get_method_name(),
            classname=test.get_classname(),
            time=test.duration,
            status=test.test_status,
        )
        if test.is_skipped():
            testcase.skipped = Skipped(message=test.get_skipped_message())
        if test.is_error():
            testcase.error = Error(
                message=test.get_error_message(),
                type=test.get_error_type(),
                error_description=test.get_failure_description()
            )
        if test.is_failure():
            testcase.failure = Failure(
                message=test.get_failure_message(),
                type=test.get_failure_type(),
                failure_description=test.get_failure_description(),
            )
        return testcase

    @classmethod
    def _get_testsuite_properties(cls, run_destination: ActionRunDestinationRecord) -> List[Property]:
        # TODO: Add more properties
        return [
            Property(name='device', value=run_destination.display_name),
        ]

    @classmethod
    def _get_action_test_suites(cls, action: ActionRecord) -> Iterator[TestSuite]:
        run_summaries = action.action_result.action_test_plan_run_summaries
        test_summaries = run_summaries.summaries if run_summaries else []
        for test_summary in test_summaries:
            for testable_summary in test_summary.testable_summaries:
                tests = testable_summary.get_tests()
                yield TestSuite(
                    name=testable_summary.name or '',
                    tests=len(tests),
                    disabled=sum(t.is_disabled() for t in tests),
                    errors=sum(t.is_error() for t in tests),
                    failures=sum(t.is_failure() for t in tests),
                    package=testable_summary.name,
                    skipped=sum(t.is_skipped() for t in tests),
                    time=sum(test.duration for test in tests),
                    timestamp=action.ended_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    testcases=[cls._get_test_case(test) for test in tests],
                    properties=cls._get_testsuite_properties(action.run_destination),
                )

    def parse_results(self) -> TestSuites:
        xcresult = self._choose_xcresult()
        invocation_record = ActionsInvocationRecord.from_xcresult(xcresult)
        test_suites = [ts for action in invocation_record.actions for ts in self._get_action_test_suites(action)]
        return TestSuites(name='', test_suites=test_suites)
