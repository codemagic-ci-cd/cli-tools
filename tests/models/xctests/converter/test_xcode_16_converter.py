from datetime import datetime
from datetime import timezone
from typing import List
from unittest import mock

import pytest
from codemagic.models.junit import Error
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuites
from codemagic.models.xctests import XcResultTool
from codemagic.models.xctests.converter import Xcode16XcResultConverter


@pytest.fixture
def expected_properties() -> List[Property]:
    return [
        Property(name="device_architecture", value="arm64"),
        Property(name="device_identifier", value="D4A58F38-8890-43BE-93F9-3D268010475D"),
        Property(name="device_name", value="iPhone SE (3rd generation)"),
        Property(name="device_operating_system", value="18.0"),
        Property(name="device_platform", value="iOS Simulator"),
        Property(name="ended_time", value="2024-10-15T00:00:00"),
        Property(name="started_time", value="2024-10-15T00:00:00"),
    ]


@pytest.fixture(autouse=True)
def patch_xcresulttool(test_results_summary_dict, test_results_tests_dict):
    mock_tests = mock.patch.object(XcResultTool, "get_test_report_tests", lambda _: test_results_tests_dict)
    mock_summary = mock.patch.object(XcResultTool, "get_test_report_summary", lambda _: test_results_summary_dict)
    with mock_tests, mock_summary:
        yield


@mock.patch("codemagic.models.xctests.converter.datetime")
def test_converter(mock_datetime, expected_properties):
    mock_datetime.fromtimestamp.return_value = datetime(2024, 10, 15, tzinfo=timezone.utc)

    test_suites: TestSuites = Xcode16XcResultConverter(...).convert()

    assert test_suites.name == "Test - banaan"
    assert test_suites.disabled == 0
    assert test_suites.errors == 3
    assert test_suites.failures is None
    assert test_suites.skipped == 1
    assert test_suites.tests == 8
    assert test_suites.time == 5.46875
    assert len(test_suites.test_suites) == 2

    ts = test_suites.test_suites[0]  # Unit tests testsuite assertions
    assert ts.disabled == 0
    assert ts.errors == 2
    assert ts.failures is None
    assert ts.name == "banaanTests [iOS 18.0 iPhone SE (3rd generation)]"
    assert ts.package == "banaanTests"
    assert ts.skipped == 1
    assert ts.tests == 6
    assert ts.time == 0.46875
    assert ts.timestamp == "2024-10-15T00:00:00"
    assert ts.properties == [*expected_properties, Property(name="title", value="banaanTests")]
    assert len(ts.testcases) == 6
    assert ts.testcases[0] == TestCase(
        classname="banaanTests",
        name="testDisabledExample()",
        status="Passed",
        time=0.0011,
    )
    assert ts.testcases[1] == TestCase(
        classname="banaanTests",
        name="testExample()",
        status="Passed",
        time=0.00045,
    )
    assert ts.testcases[2] == TestCase(
        classname="banaanTests",
        name="testExceptionExample()",
        status="Failed",
        time=0.2,
        error=Error(message='banaanTests.swift:50: failed: caught error: "badInput"', type="Error"),
    )
    assert ts.testcases[3] == TestCase(
        classname="banaanTests",
        name="testFailExample()",
        status="Failed",
        time=0.002,
        error=Error(message="banaanTests.swift:44: failed - This won't make the cut", type="Failure"),
    )
    assert ts.testcases[4] == TestCase(
        classname="banaanTests",
        name="testPerformanceExample()",
        status="Passed",
        time=0.26,
    )
    assert ts.testcases[5] == TestCase(
        classname="banaanTests",
        name="testSkippedExample()",
        status="Skipped",
        time=0.0052,
        skipped=Skipped(message="Test skipped - This test is skipped"),
    )

    ts = test_suites.test_suites[1]  # UI tests testsuite assertions
    assert ts.disabled == 0
    assert ts.errors == 1
    assert ts.failures is None
    assert ts.name == "banaanUITests [iOS 18.0 iPhone SE (3rd generation)]"
    assert ts.package == "banaanUITests"
    assert ts.skipped == 0
    assert ts.tests == 2
    assert ts.time == 5.0
    assert ts.timestamp == "2024-10-15T00:00:00"
    assert ts.properties == [*expected_properties, Property(name="title", value="banaanUITests")]

    assert len(ts.testcases) == 2
    assert ts.testcases[0] == TestCase(
        classname="banaanUITests",
        name="testUIExample()",
        status="Passed",
        time=2.0,
    )
    assert ts.testcases[1] == TestCase(
        classname="banaanUITests",
        name="testUIFailExample()",
        status="Failed",
        time=3.0,
        error=Error(message="banaanUITests.swift:40: failed - Bad UI", type="Failure"),
    )


@pytest.mark.parametrize(
    ("duration", "expected_value"),
    (
        ("0,00045s", 0.00045),
        ("0,002s", 0.002),
        ("0,0052s", 0.0052),
        ("0,26s", 0.26),
        ("0,2s", 0.2),
        ("2s", 2.0),
        ("3s", 3.0),
        ("1m 4s", 64.0),
        ("2m 26s", 146.0),
        ("5m 3s", 303.0),
        ("6m", 360.0),
    ),
)
def test_parse_xcresult_test_node_duration_value(duration, expected_value):
    value = Xcode16XcResultConverter.parse_xcresult_test_node_duration_value(duration)
    assert value == pytest.approx(expected_value)
