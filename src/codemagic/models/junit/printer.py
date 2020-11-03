from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

from codemagic.cli import Colors
from codemagic.utilities import log
from .definitions import TestSuite
from .definitions import TestSuites


class _Line:
    def __init__(self,
                 key: str,
                 value: Any,
                 key_color: Optional[Colors] = None,
                 value_color: Optional[Colors] = None):
        self._key = key
        self._value = value
        self._key_color = key_color
        self._value_color = value_color

    @property
    def key_length(self) -> int:
        return len(str(self._key))

    @property
    def value_length(self) -> int:
        return len(str(self._value))

    @classmethod
    def _get_formatted(cls, item: Any, width: int, color: Optional[Colors], align_left: bool) -> str:
        if align_left:
            s = str(item).ljust(width)
        else:
            s = str(item).rjust(width)
        return color(s) if color else s

    def get_key(self, width: int, align_left: bool = True) -> str:
        return self._get_formatted(self._key, width, self._key_color, align_left)

    def get_value(self, width: int, align_left: bool = True) -> str:
        return self._get_formatted(self._value, width, self._value_color, align_left)


class _SpacerLine(_Line):
    def __init__(self):
        super().__init__('', '')


class _HeaderLine(_Line):
    def __init__(self, header: str):
        super().__init__(header, '')

    def get_header(self) -> str:
        return str(self._key)


class _Table:

    def __init__(self,
                 lines: List[_Line],
                 vertical_separator: str = '|',
                 horizontal_separator: str = '-',
                 corner_separator: str = '+',
                 left_padding: str = '  ',
                 right_padding: str = '  ',
                 align_keys_left: bool = True,
                 align_values_left: bool = True,
                 header_color: Colors = Colors.BOLD):
        self.lines = lines or []
        self.vertical_separator = vertical_separator
        self.horizontal_separator = horizontal_separator
        self.corner_separator = corner_separator
        self.left_padding = left_padding
        self.right_padding = right_padding
        self.align_keys_left = align_keys_left
        self.align_values_left = align_values_left
        self.header_color = header_color

    def get_max_key_width(self) -> int:
        return max(line.key_length for line in self.lines)

    def get_max_value_width(self) -> int:
        return max(line.value_length for line in self.lines)

    @classmethod
    def get_header_paddings(cls, header, width: int) -> Tuple[str, str]:
        left_padding = ' ' * max(0, (width - len(header)) // 2)
        right_padding = ' ' * max(0, width - len(left_padding) - len(header))
        return left_padding, right_padding

    def get_spacer(self, width: int) -> str:
        return f'{self.corner_separator}{width * self.horizontal_separator}{self.corner_separator}'

    def construct(self) -> str:
        keys_width = self.get_max_key_width()
        values_width = self.get_max_value_width()
        total_width = sum([
            keys_width,
            values_width,
            2 * len(self.left_padding),
            2 * len(self.right_padding),
            1,  # spacer in the middle
        ])
        spacer = self.get_spacer(total_width)
        l = self.vertical_separator
        result: List[str] = []
        for line in self.lines:
            if isinstance(line, _SpacerLine):
                result.append(spacer)
            elif isinstance(line, _HeaderLine):
                header = line.get_header()
                lp, rp = self.get_header_paddings(header, total_width)
                formatted_header = f'{l}{lp}{Colors.BOLD(header)}{rp}{l}'
                result.extend([spacer, formatted_header, spacer])
            else:
                key = line.get_key(keys_width, align_left=self.align_keys_left)
                value = line.get_value(values_width, align_left=self.align_values_left)
                key = f'{self.left_padding}{key}{self.right_padding}'
                value = f'{self.left_padding}{value}{self.right_padding}'
                result.append(f'{l}{key}{l}{value}{l}')

        if result[0] != spacer:
            result.insert(0, spacer)
        if result[-1] != spacer:
            result.append(spacer)
        result.append('')

        return '\n'.join(result)


class TestSuitePrinter:

    def __init__(self, print_function: Callable[[str], None]):
        self.logger = log.get_logger(self.__class__)
        self.print = print_function

    def _print_test_suites_summary(self, test_suites: TestSuites):
        tests_color = Colors.GREEN if test_suites.tests else Colors.RED
        fails_color = Colors.RED if test_suites.failures else Colors.GREEN
        errors_color = Colors.RED if test_suites.errors else Colors.GREEN
        lines = [
            _HeaderLine('Test run summary'),
            _Line('Test suites', len(test_suites.test_suites)),
            _Line('Total tests ran', test_suites.tests, value_color=tests_color),
            _Line('Total tests failed', test_suites.failures, value_color=fails_color),
            _Line('Total tests errored', test_suites.errors, value_color=errors_color),
            _Line('Total tests skipped', test_suites.skipped)
        ]
        table = _Table(lines, align_values_left=False)
        self.print(table.construct())

    def _get_test_suite_errored_lines(self, test_suite: TestSuite) -> List[_Line]:
        def to_line(tc):
            return _Line(f'{tc.classname}.{tc.name}', self._truncate(tc.error.message))

        errored_tests = test_suite.get_errored_test_cases()
        return [_HeaderLine('Errored tests'), *map(to_line, errored_tests)] if errored_tests else []

    def _get_test_suite_failed_lines(self, test_suite: TestSuite) -> List[_Line]:
        def to_line(tc):
            return _Line(f'{tc.classname}.{tc.name}', self._truncate(tc.failure.message))

        failed_tests = test_suite.get_failed_test_cases()
        return [_HeaderLine('Failed tests'), *map(to_line, failed_tests)] if failed_tests else []

    def _get_test_suite_skipped_lines(self, test_suite: TestSuite) -> List[_Line]:
        def to_line(tc):
            return _Line(f'{tc.classname}.{tc.name}', self._truncate(tc.skipped.message))

        skipped_tests = test_suite.get_skipped_test_cases()
        return [_HeaderLine('Skipped tests'), *map(to_line, skipped_tests)] if skipped_tests else []

    def _print_test_suite(self, test_suite: TestSuite):
        tests_color = Colors.GREEN if test_suite.tests else Colors.RED
        fails_color = Colors.RED if test_suite.failures else Colors.GREEN
        errors_color = Colors.RED if test_suite.errors else Colors.GREEN

        table = _Table([
            _HeaderLine('Testsuite summary'),
            _Line('Name', test_suite.name),
            *(_Line(p.name.replace('_', ' ').title(), p.value) for p in test_suite.properties),
            _SpacerLine(),
            _Line('Total tests ran', test_suite.tests or 0, value_color=tests_color),
            _Line('Total tests failed', test_suite.failures or 0, value_color=fails_color),
            _Line('Total tests errored', test_suite.errors or 0, value_color=errors_color),
            _Line('Total tests skipped', test_suite.skipped or 0),
            *self._get_test_suite_errored_lines(test_suite),
            *self._get_test_suite_failed_lines(test_suite),
            *self._get_test_suite_skipped_lines(test_suite)
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

