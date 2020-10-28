"""
Python abstraction of JUnit format description from
https://llg.cubic.org/docs/junit/
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import NewType
from typing import Optional
from xml.etree.ElementTree import Element

Seconds = NewType('Seconds', float)


@dataclass
class TestSuites:
    name: str
    test_suites: List[TestSuite] = field(default_factory=lambda: [])

    @property
    def disabled(self) -> int:
        """ Total number of disabled tests from all testsuites. """
        return 0

    @property
    def errors(self) -> int:
        """ Total number of tests with error result from all testsuites. """
        return 0

    @property
    def failures(self) -> int:
        """ Total number of failed tests from all testsuites. """
        return 0

    @property
    def tests(self) -> int:
        """ Total number of tests from all testsuites. """
        return sum(suite.tests for suite in self.test_suites)

    @property
    def time(self) -> float:
        """ Time in seconds to execute all test suites. """
        return 0

    def to_xml(self) -> Element:
        extras = {
            'disabled': self.disabled,
            'errors': self.errors,
            'failures': self.failures,
            'time': self.time,
        }
        root = Element(
            'testsuites',
            attrib={'name': self.name, 'tests': str(self.tests)},
            **{k: str(v) for k, v in extras.items() if v})

        root.extend([test_suite.to_xml() for test_suite in self.test_suites])

        return root


@dataclass
class TestSuite:
    name: str  # Full (class) name of the test for non-aggregated testsuite documents.
    tests: int  # The total number of tests in the suite.
    disabled: Optional[int] = None  # The total number of disabled tests in the suite.
    errors: Optional[int] = None  # The total number of tests in the suite that errored.
    failures: Optional[int] = None  # The total number of tests in the suite that failed.
    package: Optional[str] = None  # Derived from testsuite/@name in the non-aggregated documents.
    skipped: Optional[int] = None  # The total number of skipped tests.
    time: Optional[Seconds] = None  # Time taken (in seconds) to execute the tests in the suite.
    timestamp: Optional[str] = None  # When the test was executed in ISO 8601 format (2014-01-21T16:17:18).
    properties: List[Property] = field(default_factory=lambda: [])
    testcases: List[TestCase] = field(default_factory=lambda: [])

    def to_xml(self) -> Element:
        element = Element(
            'testsuite',
            attrib={'name': self.name, 'tests': str(self.tests)}
        )
        # TODO: ...
        return element


@dataclass
class Property:
    name: str
    value: str


@dataclass
class TestCase:
    classname: str  # Full class name for the class the test method is in.
    name: str  # Name of the test method
    assertions: Optional[int] = None  # Number of assertions in the test case.
    status: Optional[str] = None
    time: Optional[Seconds] = None  # Time taken (in seconds) to execute the test.
    error: Optional[Error] = None
    failure: Optional[Failure] = None
    skipped: Optional[Skipped] = None


@dataclass
class Skipped:
    message: str = ''  # Message / description why the test case was skipped.


@dataclass
class Error:
    """
    Error indicates that the test errored.
    An errored test had an unanticipated problem.
    For example an unchecked throwable (exception), crash or a problem with the implementation of the test.
    Contains as a text node relevant data for the error, for example a stack trace.
    """
    message: str  # The error message. e.g., if a java exception is thrown, the return value of getMessage()
    type: str  # The type of error that occurred (if a java exception is thrown the full class name of the exception).
    error_description: Optional[str] = None


@dataclass
class Failure:
    """
    Failure indicates that the test failed.
    A failure is a condition which the code has explicitly failed by using the mechanisms for that purpose.
    For example via an assertEquals.
    Contains as a text node relevant data for the failure, e.g., a stack trace.
    """
    message: str  # The message specified in the assert.
    type: str  # The type of the assert.
    error_description: Optional[str] = None
