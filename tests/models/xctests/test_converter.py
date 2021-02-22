import json
import pathlib
import string
from typing import Any
from typing import Dict
from unittest import mock

import pytest

from codemagic.models.junit import Error
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuites
from codemagic.models.xctests import XcResultConverter
from codemagic.models.xctests import XcResultTool


def _mock_get_object(_xcresult: pathlib.Path, object_id: str) -> Dict[str, Any]:
    valid_chars = f'-_.{string.ascii_letters}{string.digits}'
    filename = ''.join(c if c in valid_chars else '_' for c in object_id)
    mock_path = pathlib.Path(__file__).parent / 'mocks' / f'{filename}.json'
    if not mock_path.exists():
        raise ValueError(f'Cannot mock object with ID {object_id!r}')
    return json.loads(mock_path.read_text())


@pytest.fixture()
def testsuite_properties():
    return [
        Property(name='device_architecture', value='x86_64'),
        Property(name='device_identifier', value='7C2AC071-3FAE-4370-81D8-079BC87CC391'),
        Property(name='device_name', value='iPhone 8'),
        Property(name='device_operating_system', value='13.2.2 (17B102)'),
        Property(name='device_platform', value='iOS Simulator'),
        Property(name='ended_time', value='2020-10-29T15:35:53'),
        Property(name='started_time', value='2020-10-29T15:33:18'),
        Property(name='title', value='Testing project banaan with scheme banaan'),
    ]


@pytest.fixture()
def expected_unit_testcases():
    return [
        TestCase(
            classname='banaanTests',
            name='testExample()',
            assertions=None,
            status='Success',
            time=0.002252936363220215,
            error=None,
            failure=None,
            skipped=None,
        ),
        TestCase(
            classname='banaanTests',
            name='testExceptionExample()',
            assertions=None, status='Failure',
            time=0.02912592887878418,
            error=Error(
                message='failed: caught error: "The operation couldn’t be completed. (banaanTests.MyErrors error 0.)"',
                type='banaanTests.MyErrors',
                error_description=(
                    'failed: caught error: "The operation couldn’t be completed. (banaanTests.MyErrors error 0.)"\n'
                    'Thrown Error: failed: caught error: "The operation couldn’t be completed. '
                    '(banaanTests.MyErrors error 0.)"'
                ),
            ),
            failure=None,
            skipped=None,
        ),
        TestCase(
            classname='banaanTests',
            name='testFailExample()',
            assertions=None,
            status='Failure',
            time=0.03098905086517334,
            error=None,
            failure=Failure(
                message="failed - This won't make the cut", type='Assertion Failure',
                failure_description=(
                    '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:44 failed - '
                    "This won't make the cut\n"
                    "Assertion Failure at banaanTests.swift:44: failed - This won't make the cut"
                ),
            ),
            skipped=None,
        ),
        TestCase(
            classname='banaanTests',
            name='testPerformanceExample()',
            assertions=None,
            status='Success',
            time=0.2531629800796509,
            error=None,
            failure=None,
            skipped=None,
        ),
        TestCase(
            classname='banaanTests',
            name='testSkippedExample()',
            assertions=None,
            status='Skipped',
            time=0.0028339624404907227,
            error=None,
            failure=None,
            skipped=Skipped(
                message=(
                    '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:34 Test skipped'
                    ' - This test is skipped'
                ),
            ),
        ),
    ]


@pytest.fixture()
def expected_ui_testcases():
    return [
        TestCase(
            classname='banaanUITests',
            name='testUIExample()',
            assertions=None,
            status='Success',
            time=1.7065880298614502,
            error=None,
            failure=None,
            skipped=None,
        ),
        TestCase(
            classname='banaanUITests',
            name='testUIFailExample()',
            assertions=None,
            status='Failure',
            time=2.6687620878219604,
            error=None,
            failure=Failure(
                message='failed - Bad UI',
                type='Assertion Failure',
                failure_description=(
                    '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2UITests/banaanUITests.swift:40 failed'
                    ' - Bad UI\n'
                    'Start Test at 2020-10-29 15:34:26.057\n'
                    'Set Up\n'
                    '    Open io.codemagic.banaan\n'
                    '        Launch io.codemagic.banaan\n'
                    '            Terminate io.codemagic.banaan:57014\n'
                    '            Setting up automation session\n'
                    '            Wait for io.codemagic.banaan to idle\n'
                    'Assertion Failure at banaanUITests.swift:40: failed - Bad UI\n'
                    'Tear Down'
                ),
            ),
            skipped=None,
        ),
    ]


@mock.patch.object(XcResultTool, 'get_object', _mock_get_object)
def test_converter(action_invocations_record, expected_ui_testcases, expected_unit_testcases, testsuite_properties):
    test_suites: TestSuites = XcResultConverter.actions_invocation_record_to_junit(action_invocations_record)

    # Full XML assertions
    assert test_suites.disabled == 0
    assert test_suites.errors == 2
    assert test_suites.failures == 4
    assert test_suites.name == ''
    assert test_suites.skipped == 2
    assert test_suites.tests == 14
    assert test_suites.time == 10.096374988555908
    assert len(test_suites.test_suites) == 4

    ts = test_suites.test_suites[0]  # Unit tests testsuite assertions
    assert ts.disabled == 0
    assert ts.errors == 1
    assert ts.failures == 1
    assert ts.name == 'banaanTests [iOS 13.2.2 iPhone 8]'
    assert ts.package == 'banaanTests'
    assert ts.skipped == 1
    assert ts.tests == 5
    assert ts.time == 0.31836485862731934
    assert ts.timestamp == '2020-10-29T15:35:53'
    assert ts.properties == testsuite_properties
    assert ts.testcases == expected_unit_testcases

    ts = test_suites.test_suites[1]  # UI tests testsuite assertions
    assert ts.disabled == 0
    assert ts.errors == 0
    assert ts.failures == 1
    assert ts.name == 'banaanUITests [iOS 13.2.2 iPhone 8]'
    assert ts.package == 'banaanUITests'
    assert ts.skipped == 0
    assert ts.tests == 2
    assert ts.time == 4.375350117683411
    assert ts.timestamp == '2020-10-29T15:35:53'
    assert ts.properties == testsuite_properties
    assert ts.testcases == expected_ui_testcases
