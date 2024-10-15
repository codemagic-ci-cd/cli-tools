from datetime import datetime
from datetime import timezone
from typing import List
from unittest import mock

import pytest
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuites
from codemagic.models.xctests import XcResultTool
from codemagic.models.xctests.converter import Xcode16XcResultConverter


def _get_test_report_tests(_):
    return {
        "devices": [
            {
                "architecture": "arm64",
                "deviceId": "D4A58F38-8890-43BE-93F9-3D268010475D",
                "deviceName": "iPhone SE (3rd generation)",
                "modelName": "iPhone SE (3rd generation)",
                "osVersion": "18.0",
                "platform": "iOS Simulator",
            },
        ],
        "testNodes": [
            {
                "children": [
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "duration": "0,0011s",
                                        "name": "testDisabledExample()",
                                        "nodeIdentifier": "banaanTests/testDisabledExample()",
                                        "nodeType": "Test Case",
                                        "result": "Passed",
                                    },
                                    {
                                        "duration": "0,00045s",
                                        "name": "testExample()",
                                        "nodeIdentifier": "banaanTests/testExample()",
                                        "nodeType": "Test Case",
                                        "result": "Passed",
                                    },
                                    {
                                        "children": [
                                            {
                                                "name": 'banaanTests.swift:50: failed: caught error: "badInput"',
                                                "nodeType": "Failure Message",
                                                "result": "Failed",
                                            },
                                        ],
                                        "duration": "0,2s",
                                        "name": "testExceptionExample()",
                                        "nodeIdentifier": "banaanTests/testExceptionExample()",
                                        "nodeType": "Test Case",
                                        "result": "Failed",
                                    },
                                    {
                                        "children": [
                                            {
                                                "name": "banaanTests.swift:44: failed - This won't make the cut",
                                                "nodeType": "Failure Message",
                                                "result": "Failed",
                                            },
                                        ],
                                        "duration": "0,002s",
                                        "name": "testFailExample()",
                                        "nodeIdentifier": "banaanTests/testFailExample()",
                                        "nodeType": "Test Case",
                                        "result": "Failed",
                                    },
                                    {
                                        "duration": "0,26s",
                                        "name": "testPerformanceExample()",
                                        "nodeIdentifier": "banaanTests/testPerformanceExample()",
                                        "nodeType": "Test Case",
                                        "result": "Passed",
                                    },
                                    {
                                        "children": [
                                            {
                                                "name": "Test skipped - This test is skipped",
                                                "nodeType": "Failure Message",
                                                "result": "Skipped",
                                            },
                                        ],
                                        "duration": "0,0052s",
                                        "name": "testSkippedExample()",
                                        "nodeIdentifier": "banaanTests/testSkippedExample()",
                                        "nodeType": "Test Case",
                                        "result": "Skipped",
                                    },
                                ],
                                "name": "banaanTests",
                                "nodeType": "Test Suite",
                                "result": "Failed",
                            },
                        ],
                        "name": "banaanTests",
                        "nodeType": "Unit test bundle",
                        "result": "Failed",
                    },
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "duration": "2s",
                                        "name": "testUIExample()",
                                        "nodeIdentifier": "banaanUITests/testUIExample()",
                                        "nodeType": "Test Case",
                                        "result": "Passed",
                                    },
                                    {
                                        "children": [
                                            {
                                                "name": "banaanUITests.swift:40: failed - Bad UI",
                                                "nodeType": "Failure Message",
                                                "result": "Failed",
                                            },
                                        ],
                                        "duration": "3s",
                                        "name": "testUIFailExample()",
                                        "nodeIdentifier": "banaanUITests/testUIFailExample()",
                                        "nodeType": "Test Case",
                                        "result": "Failed",
                                    },
                                ],
                                "name": "banaanUITests",
                                "nodeType": "Test Suite",
                                "result": "Failed",
                            },
                        ],
                        "name": "banaanUITests",
                        "nodeType": "UI test bundle",
                        "result": "Failed",
                    },
                ],
                "name": "banaan",
                "nodeType": "Test Plan",
                "result": "Failed",
            },
        ],
        "testPlanConfigurations": [
            {
                "configurationId": "1",
                "configurationName": "Test Scheme Action",
            },
        ],
    }


def _get_test_report_summary(_):
    return {
        "devicesAndConfigurations": [
            {
                "device": {
                    "architecture": "arm64",
                    "deviceId": "D4A58F38-8890-43BE-93F9-3D268010475D",
                    "deviceName": "iPhone SE (3rd generation)",
                    "modelName": "iPhone SE (3rd generation)",
                    "osVersion": "18.0",
                    "platform": "iOS Simulator",
                },
                "expectedFailures": 0,
                "failedTests": 3,
                "passedTests": 4,
                "skippedTests": 1,
                "testPlanConfiguration": {
                    "configurationId": "1",
                    "configurationName": "Test Scheme Action",
                },
            },
        ],
        "environmentDescription": "banaan · Built with macOS 14.7",
        "expectedFailures": 0,
        "failedTests": 3,
        "finishTime": 1728473305.128,
        "passedTests": 4,
        "result": "Failed",
        "skippedTests": 1,
        "startTime": 1728473222.071,
        "statistics": [
            {
                "subtitle": "1 test run",
                "title": "1 test collected performance metrics",
            },
        ],
        "testFailures": [
            {
                "failureText": 'failed: caught error: "badInput"',
                "targetName": "banaanTests",
                "testIdentifier": 3,
                "testName": "testExceptionExample()",
            },
            {
                "failureText": "failed - This won't make the cut",
                "targetName": "banaanTests",
                "testIdentifier": 4,
                "testName": "testFailExample()",
            },
            {
                "failureText": "failed - Bad UI",
                "targetName": "banaanUITests",
                "testIdentifier": 8,
                "testName": "testUIFailExample()",
            },
        ],
        "title": "Test - banaan",
        "topInsights": [],
        "totalTestCount": 8,
    }


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


@mock.patch.object(XcResultTool, "get_test_report_tests", _get_test_report_tests)
@mock.patch.object(XcResultTool, "get_test_report_summary", _get_test_report_summary)
@mock.patch("codemagic.models.xctests.converter.datetime")
def test_converter(mock_datetime, expected_properties):
    mock_datetime.fromtimestamp.return_value = datetime(2024, 10, 15, tzinfo=timezone.utc)

    test_suites: TestSuites = Xcode16XcResultConverter(...).convert()

    assert test_suites.name == "Test - banaan"
    assert test_suites.disabled == 0
    assert test_suites.errors is None
    assert test_suites.failures == 3
    assert test_suites.skipped == 1
    assert test_suites.tests == 8
    assert test_suites.time == 5.46875
    assert len(test_suites.test_suites) == 2

    ts = test_suites.test_suites[0]  # Unit tests testsuite assertions
    assert ts.disabled == 0
    assert ts.errors is None
    assert ts.failures == 2
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
        failure=Failure(message='banaanTests.swift:50: failed: caught error: "badInput"', type="Error"),
    )
    assert ts.testcases[3] == TestCase(
        classname="banaanTests",
        name="testFailExample()",
        status="Failed",
        time=0.002,
        failure=Failure(message="banaanTests.swift:44: failed - This won't make the cut", type="Failure"),
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
    assert ts.errors is None
    assert ts.failures == 1
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
        failure=Failure(message="banaanUITests.swift:40: failed - Bad UI", type="Failure"),
    )
