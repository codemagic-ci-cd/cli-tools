import pathlib
from unittest import mock

import pytest
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuite
from codemagic.models.junit import TestSuites
from codemagic.models.xctests import XcResultTool
from codemagic.models.xctests.converter import Xcode16XcResultConverter


@pytest.fixture
def xcresult() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "mocks" / "Test.xcresult"


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


@mock.patch.object(XcResultTool, "get_test_report_tests", _get_test_report_tests)
@mock.patch.object(XcResultTool, "get_test_report_summary", _get_test_report_summary)
def test_converter(xcresult):
    test_suites: TestSuites = Xcode16XcResultConverter(xcresult).convert()

    expected_test_suites = TestSuites(
        name="Test - banaan",
        test_suites=[
            TestSuite(
                name="banaanTests [iOS 18.0 iPhone SE (3rd generation)]",
                tests=6,
                disabled=0,
                errors=0,
                failures=2,
                package="banaanTests",
                skipped=1,
                time=0.46875,
                timestamp="2024-10-09T14:28:25",
                properties=[
                    Property(name="device_architecture", value="arm64"),
                    Property(name="device_identifier", value="D4A58F38-8890-43BE-93F9-3D268010475D"),
                    Property(name="device_name", value="iPhone SE (3rd generation)"),
                    Property(name="device_operating_system", value="18.0"),
                    Property(name="device_platform", value="iOS Simulator"),
                    Property(name="ended_time", value="2024-10-09T14:28:25"),
                    Property(name="started_time", value="2024-10-09T14:27:02"),
                    Property(name="title", value="banaanTests"),
                ],
                testcases=[
                    TestCase(
                        classname="banaanTests",
                        name="testDisabledExample()",
                        assertions=None,
                        status="Passed",
                        time=0.0011,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanTests",
                        name="testExample()",
                        assertions=None,
                        status="Passed",
                        time=0.00045,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanTests",
                        name="testExceptionExample()",
                        assertions=None,
                        status="Failed",
                        time=0.2,
                        error=None,
                        failure=Failure(
                            message='banaanTests.swift:50: failed: caught error: "badInput"',
                            type="Error",
                            failure_description=None,
                        ),
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanTests",
                        name="testFailExample()",
                        assertions=None,
                        status="Failed",
                        time=0.002,
                        error=None,
                        failure=Failure(
                            message="banaanTests.swift:44: failed - This won't make the cut",
                            type="Failure",
                            failure_description=None,
                        ),
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanTests",
                        name="testPerformanceExample()",
                        assertions=None,
                        status="Passed",
                        time=0.26,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanTests",
                        name="testSkippedExample()",
                        assertions=None,
                        status="Skipped",
                        time=0.0052,
                        error=None,
                        failure=None,
                        skipped=Skipped(message="Test skipped - This test is skipped"),
                    ),
                ],
            ),
            TestSuite(
                name="banaanUITests [iOS 18.0 iPhone SE (3rd generation)]",
                tests=2,
                disabled=0,
                errors=0,
                failures=1,
                package="banaanUITests",
                skipped=0,
                time=5.0,
                timestamp="2024-10-09T14:28:25",
                properties=[
                    Property(name="device_architecture", value="arm64"),
                    Property(name="device_identifier", value="D4A58F38-8890-43BE-93F9-3D268010475D"),
                    Property(name="device_name", value="iPhone SE (3rd generation)"),
                    Property(name="device_operating_system", value="18.0"),
                    Property(name="device_platform", value="iOS Simulator"),
                    Property(name="ended_time", value="2024-10-09T14:28:25"),
                    Property(name="started_time", value="2024-10-09T14:27:02"),
                    Property(name="title", value="banaanUITests"),
                ],
                testcases=[
                    TestCase(
                        classname="banaanUITests",
                        name="testUIExample()",
                        assertions=None,
                        status="Passed",
                        time=2.0,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname="banaanUITests",
                        name="testUIFailExample()",
                        assertions=None,
                        status="Failed",
                        time=3.0,
                        error=None,
                        failure=Failure(
                            message="banaanUITests.swift:40: failed - Bad UI",
                            type="Failure",
                            failure_description=None,
                        ),
                        skipped=None,
                    ),
                ],
            ),
        ],
    )

    assert test_suites == expected_test_suites
