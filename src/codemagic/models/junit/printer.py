from typing import Callable
from typing import List

from codemagic.cli import Colors
from codemagic.models.table import Header
from codemagic.models.table import Line
from codemagic.models.table import Spacer
from codemagic.models.table import Table
from codemagic.utilities import log

from .definitions import TestSuite
from .definitions import TestSuites


class TestSuitePrinter:

    def __init__(self, print_function: Callable[[str], None]):
        self.logger = log.get_logger(self.__class__)
        self.print = print_function

    def _print_test_suites_summary(self, test_suites: TestSuites):
        tests_color = Colors.GREEN if test_suites.tests else Colors.RED
        fails_color = Colors.RED if test_suites.failures else Colors.GREEN
        errors_color = Colors.RED if test_suites.errors else Colors.GREEN
        table = Table([
            Header('Test run summary'),
            Line('Test suites', len(test_suites.test_suites)),
            Line('Total tests ran', test_suites.tests, value_color=tests_color),
            Line('Total tests failed', test_suites.failures, value_color=fails_color),
            Line('Total tests errored', test_suites.errors, value_color=errors_color),
            Line('Total tests skipped', test_suites.skipped),
        ], align_values_left=False)
        self.print(table.construct())

    def _get_test_suite_errored_lines(self, test_suite: TestSuite) -> List[Line]:
        def to_line(tc):
            return Line(f'{tc.classname}.{tc.name}', self._truncate(tc.error.message))

        errored_tests = test_suite.get_errored_test_cases()
        return [Header('Errored tests'), *map(to_line, errored_tests)] if errored_tests else []

    def _get_test_suite_failed_lines(self, test_suite: TestSuite) -> List[Line]:
        def to_line(tc):
            return Line(f'{tc.classname}.{tc.name}', self._truncate(tc.failure.message))

        failed_tests = test_suite.get_failed_test_cases()
        return [Header('Failed tests'), *map(to_line, failed_tests)] if failed_tests else []

    def _get_test_suite_skipped_lines(self, test_suite: TestSuite) -> List[Line]:
        def to_line(tc):
            return Line(f'{tc.classname}.{tc.name}', self._truncate(tc.skipped.message))

        skipped_tests = test_suite.get_skipped_test_cases()
        return [Header('Skipped tests'), *map(to_line, skipped_tests)] if skipped_tests else []

    def _print_test_suite(self, test_suite: TestSuite):
        tests_color = Colors.GREEN if test_suite.tests else Colors.RED
        fails_color = Colors.RED if test_suite.failures else Colors.GREEN
        errors_color = Colors.RED if test_suite.errors else Colors.GREEN

        table = Table([
            Header('Testsuite summary'),
            Line('Name', test_suite.name),
            *(Line(p.name.replace('_', ' ').title(), p.value) for p in test_suite.properties),
            Spacer(),
            Line('Total tests ran', test_suite.tests or 0, value_color=tests_color),
            Line('Total tests failed', test_suite.failures or 0, value_color=fails_color),
            Line('Total tests errored', test_suite.errors or 0, value_color=errors_color),
            Line('Total tests skipped', test_suite.skipped or 0),
            *self._get_test_suite_errored_lines(test_suite),
            *self._get_test_suite_failed_lines(test_suite),
            *self._get_test_suite_skipped_lines(test_suite),
        ])

        self.print(table.construct())

    @classmethod
    def _truncate(cls, s: str, max_width: int = 80) -> str:
        t = s[:max_width]
        return t if s == t else f'{t}...'

    def print_test_suites(self, test_suites: TestSuites):
        for test_suite in sorted(test_suites.test_suites, key=lambda ts: ts.name):
            self._print_test_suite(test_suite)

        self._print_test_suites_summary(test_suites)
