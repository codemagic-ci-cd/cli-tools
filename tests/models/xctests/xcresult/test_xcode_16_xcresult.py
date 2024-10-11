import json
from typing import Dict

import pytest
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcDevice
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcDevicesAndConfigurations
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestBundle
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestCase
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestCaseDetail
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestDetails
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestFailure
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestPlan
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestPlanConfiguration
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestResultsSummary
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestResultsTests
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestRun
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestRunAction
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestStatistic
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestSuite


@pytest.fixture
def test_results_summary_dict(mocks_dir) -> Dict:
    mock_path = mocks_dir / "test_results_summary.json"
    return json.loads(mock_path.read_text())


@pytest.fixture
def test_results_tests_dict(mocks_dir) -> Dict:
    mock_path = mocks_dir / "test_results_tests.json"
    return json.loads(mock_path.read_text())


@pytest.fixture
def test_results_test_detail_dict(mocks_dir) -> Dict:
    mock_path = mocks_dir / "test_results_test_details.json"
    return json.loads(mock_path.read_text())


def test_load_test_results_summary(test_results_summary_dict):
    test_results_summary = XcTestResultsSummary.from_dict(test_results_summary_dict)

    expected_test_results_summary = XcTestResultsSummary(
        devices_and_configurations=[
            XcDevicesAndConfigurations(
                device=XcDevice(
                    architecture="arm64",
                    device_id="D4A58F38-8890-43BE-93F9-3D268010475D",
                    device_name="iPhone SE (3rd generation)",
                    model_name="iPhone SE (3rd generation)",
                    os_version="18.0",
                    platform="iOS Simulator",
                ),
                expected_failures=0,
                failed_tests=3,
                passed_tests=4,
                skipped_tests=1,
                test_plan_configuration=XcTestPlanConfiguration(
                    configuration_id="1",
                    configuration_name="Test Scheme Action",
                ),
            ),
        ],
        environment_description="banaan · Built with macOS 14.7",
        expected_failures=0,
        failed_tests=3,
        finish_time=1728473305.128,
        passed_tests=4,
        result="Failed",
        skipped_tests=1,
        start_time=1728473222.071,
        statistics=[
            XcTestStatistic(
                subtitle="1 test run",
                title="1 test collected performance metrics",
            ),
        ],
        test_failures=[
            XcTestFailure(
                failure_text='failed: caught error: "badInput"',
                target_name="banaanTests",
                test_identifier=3,
                test_name="testExceptionExample()",
            ),
            XcTestFailure(
                failure_text="failed - This won't make the cut",
                target_name="banaanTests",
                test_identifier=4,
                test_name="testFailExample()",
            ),
            XcTestFailure(
                failure_text="failed - Bad UI",
                target_name="banaanUITests",
                test_identifier=8,
                test_name="testUIFailExample()",
            ),
        ],
        title="Test - banaan",
        top_insights=[],
        total_test_count=8,
    )

    assert test_results_summary == expected_test_results_summary


def test_load_test_results_tests(test_results_tests_dict):
    test_results_tests = XcTestResultsTests.from_dict(test_results_tests_dict)

    expected_test_results_tests = XcTestResultsTests(
        devices=[
            XcDevice(
                architecture="arm64",
                device_id="D4A58F38-8890-43BE-93F9-3D268010475D",
                device_name="iPhone SE (3rd generation)",
                model_name="iPhone SE (3rd generation)",
                os_version="18.0",
                platform="iOS Simulator",
            ),
        ],
        test_plans=[
            XcTestPlan(
                name="banaan",
                node_type="Test Plan",
                result="Failed",
                test_bundles=[
                    XcTestBundle(
                        name="banaanTests",
                        node_type="Unit test bundle",
                        result="Failed",
                        test_suites=[
                            XcTestSuite(
                                name="banaanTests",
                                node_type="Test Suite",
                                result="Failed",
                                test_cases=[
                                    XcTestCase(
                                        name="testDisabledExample()",
                                        node_type="Test Case",
                                        result="Passed",
                                        duration="0,0011s",
                                        node_identifier="banaanTests/testDisabledExample()",
                                        details=[],
                                    ),
                                    XcTestCase(
                                        name="testExample()",
                                        node_type="Test Case",
                                        result="Passed",
                                        duration="0,00045s",
                                        node_identifier="banaanTests/testExample()",
                                        details=[],
                                    ),
                                    XcTestCase(
                                        name="testExceptionExample()",
                                        node_type="Test Case",
                                        result="Failed",
                                        duration="0,2s",
                                        node_identifier="banaanTests/testExceptionExample()",
                                        details=[
                                            XcTestCaseDetail(
                                                name='banaanTests.swift:50: failed: caught error: "badInput"',
                                                node_type="Failure Message",
                                                result="Failed",
                                            ),
                                        ],
                                    ),
                                    XcTestCase(
                                        name="testFailExample()",
                                        node_type="Test Case",
                                        result="Failed",
                                        duration="0,002s",
                                        node_identifier="banaanTests/testFailExample()",
                                        details=[
                                            XcTestCaseDetail(
                                                name="banaanTests.swift:44: failed - This won't make the cut",
                                                node_type="Failure Message",
                                                result="Failed",
                                            ),
                                        ],
                                    ),
                                    XcTestCase(
                                        name="testPerformanceExample()",
                                        node_type="Test Case",
                                        result="Passed",
                                        duration="0,26s",
                                        node_identifier="banaanTests/testPerformanceExample()",
                                        details=[],
                                    ),
                                    XcTestCase(
                                        name="testSkippedExample()",
                                        node_type="Test Case",
                                        result="Skipped",
                                        duration="0,0052s",
                                        node_identifier="banaanTests/testSkippedExample()",
                                        details=[
                                            XcTestCaseDetail(
                                                name="Test skipped - This test is skipped",
                                                node_type="Failure Message",
                                                result="Skipped",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    XcTestBundle(
                        name="banaanUITests",
                        node_type="UI test bundle",
                        result="Failed",
                        test_suites=[
                            XcTestSuite(
                                name="banaanUITests",
                                node_type="Test Suite",
                                result="Failed",
                                test_cases=[
                                    XcTestCase(
                                        name="testUIExample()",
                                        node_type="Test Case",
                                        result="Passed",
                                        duration="2s",
                                        node_identifier="banaanUITests/testUIExample()",
                                        details=[],
                                    ),
                                    XcTestCase(
                                        name="testUIFailExample()",
                                        node_type="Test Case",
                                        result="Failed",
                                        duration="3s",
                                        node_identifier="banaanUITests/testUIFailExample()",
                                        details=[
                                            XcTestCaseDetail(
                                                name="banaanUITests.swift:40: failed - Bad UI",
                                                node_type="Failure Message",
                                                result="Failed",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        test_plan_configurations=[
            XcTestPlanConfiguration(configuration_id="1", configuration_name="Test Scheme Action"),
        ],
    )

    assert test_results_tests == expected_test_results_tests


def test_load_test_results_test_details(test_results_test_detail_dict):
    test_details = XcTestDetails.from_dict(test_results_test_detail_dict)

    expected_test_details = XcTestDetails(
        devices=[
            XcDevice(
                architecture="arm64",
                device_id="D4A58F38-8890-43BE-93F9-3D268010475D",
                device_name="iPhone SE (3rd generation)",
                model_name="iPhone SE (3rd generation)",
                os_version="18.0",
                platform="iOS Simulator",
            ),
        ],
        duration="Ran for 2,6 seconds",
        has_media_attachments=False,
        has_performance_metrics=False,
        start_time=1728473285.429,
        test_description="Test case with 1 run",
        test_identifier="banaanUITests/testUIExample()",
        test_name="testUIExample()",
        test_plan_configurations=[
            XcTestPlanConfiguration(
                configuration_id="1",
                configuration_name="Test Scheme Action",
            ),
        ],
        test_result="Passed",
        test_runs=[
            XcTestRun(
                name="iPhone SE (3rd generation)",
                node_type="Device",
                result="Passed",
                test_run_actions=[
                    XcTestRunAction(
                        name="Test Scheme Action",
                        node_type="Test Plan Configuration",
                        result="Passed",
                        duration="2s",
                        node_identifier="1",
                    ),
                ],
                details="iOS Simulator 18.0",
                duration="2s",
                node_identifier="D4A58F38-8890-43BE-93F9-3D268010475D",
            ),
        ],
    )

    assert test_details == expected_test_details
