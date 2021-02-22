"""
Python abstraction of JUnit format description from
https://llg.cubic.org/docs/junit/
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement


@dataclass
class TestSuites:
    name: str
    test_suites: List[TestSuite] = field(default_factory=lambda: [])

    __test__ = False  # Tell Pytest not to collect this class as test

    @property
    def disabled(self) -> int:
        """ Total number of disabled tests from all testsuites. """
        return sum(suite.disabled for suite in self.test_suites if suite.disabled)

    @property
    def errors(self) -> int:
        """ Total number of tests with error result from all testsuites. """
        return sum(suite.errors for suite in self.test_suites if suite.errors)

    @property
    def failures(self) -> int:
        """ Total number of failed tests from all testsuites. """
        return sum(suite.failures for suite in self.test_suites if suite.failures)

    @property
    def tests(self) -> int:
        """ Total number of tests from all testsuites. """
        return sum(suite.tests for suite in self.test_suites)

    @property
    def skipped(self) -> int:
        """ Total number of tests from all testsuites. """
        return sum((suite.skipped or 0) for suite in self.test_suites)

    @property
    def time(self) -> float:
        """ Time in seconds to execute all test suites. """
        return sum(suite.time for suite in self.test_suites if suite.time)

    def as_xml(self) -> Element:
        extras = {
            'disabled': self.disabled,
            'errors': self.errors,
            'failures': self.failures,
            'time': self.time,
        }
        root = Element(
            'testsuites',
            attrib={'name': self.name, 'tests': str(self.tests)},
            **{k: str(v) for k, v in extras.items() if v},
        )
        root.extend([test_suite.as_xml() for test_suite in self.test_suites])
        return root

    def save_xml(self, xml_path: pathlib.Path):
        xml_str = ElementTree.tostring(self.as_xml())
        pretty_xml = minidom.parseString(xml_str).toprettyxml()
        xml_path.write_text(pretty_xml)


@dataclass
class TestSuite:
    name: str  # Full (class) name of the test for non-aggregated testsuite documents.
    tests: int  # The total number of tests in the suite.
    disabled: Optional[int] = None  # The total number of disabled tests in the suite.
    errors: Optional[int] = None  # The total number of tests in the suite that errored.
    failures: Optional[int] = None  # The total number of tests in the suite that failed.
    package: Optional[str] = None  # Derived from testsuite/@name in the non-aggregated documents.
    skipped: Optional[int] = None  # The total number of skipped tests.
    time: Optional[float] = None  # Time taken (in seconds) to execute the tests in the suite.
    timestamp: Optional[str] = None  # When the test was executed in ISO 8601 format (2014-01-21T16:17:18).
    properties: List[Property] = field(default_factory=lambda: [])
    testcases: List[TestCase] = field(default_factory=lambda: [])

    __test__ = False  # Tell Pytest not to collect this class as test

    def get_errored_test_cases(self) -> List[TestCase]:
        return [tc for tc in self.testcases if tc.error]

    def get_failed_test_cases(self) -> List[TestCase]:
        return [tc for tc in self.testcases if tc.failure]

    def get_skipped_test_cases(self) -> List[TestCase]:
        return [tc for tc in self.testcases if tc.skipped]

    def as_xml(self) -> Element:
        extras = {
            'disabled': self.disabled,
            'errors': self.errors,
            'failures': self.failures,
            'package': self.package,
            'skipped': self.skipped,
            'time': self.time,
            'timestamp': self.timestamp,
        }
        element = Element(
            'testsuite',
            attrib={'name': self.name, 'tests': str(self.tests)},
            **{k: str(v) for k, v in extras.items() if v},
        )
        if self.properties:
            properties = SubElement(element, 'properties')
            properties.extend([p.as_xml() for p in self.properties])
        element.extend([tc.as_xml() for tc in self.testcases])
        return element


@dataclass
class Property:
    name: str
    value: str

    def as_xml(self) -> Element:
        return Element('property', attrib={'name': self.name, 'value': str(self.value)})


@dataclass
class TestCase:
    classname: str  # Full class name for the class the test method is in.
    name: str  # Name of the test method
    assertions: Optional[int] = None  # Number of assertions in the test case.
    status: Optional[str] = None
    time: Optional[float] = None  # Time taken (in seconds) to execute the test.
    error: Optional[Error] = None
    failure: Optional[Failure] = None
    skipped: Optional[Skipped] = None

    __test__ = False  # Tell Pytest not to collect this class as test

    def as_xml(self) -> Element:
        extras = {
            'time': self.time,
            'status': self.status,
            'assertions': self.assertions,
        }
        element = Element(
            'testcase',
            attrib={'name': self.name, 'classname': self.classname},
            **{k: str(v) for k, v in extras.items() if v},
        )
        if self.error:
            element.append(self.error.as_xml())
        if self.failure:
            element.append(self.failure.as_xml())
        if self.skipped:
            element.append(self.skipped.as_xml())
        return element


@dataclass
class Skipped:
    message: str = ''  # Message / description why the test case was skipped.

    def as_xml(self):
        return Element('skipped', attrib={'message': self.message})


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

    def as_xml(self):
        element = Element('error', attrib={'message': self.message, 'type': self.type})
        if self.error_description:
            element.text = self.error_description
        return element


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
    failure_description: Optional[str] = None

    def as_xml(self):
        element = Element('failure', attrib={'message': self.message, 'type': self.type})
        if self.failure_description:
            element.text = self.failure_description
        return element
