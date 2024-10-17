from codemagic.models.xctests.xcresult import XcTestNode
from codemagic.models.xctests.xcresult import XcTestNodeType
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcConfiguration
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcDevice
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcSummary
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestFailure
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestPlanConfiguration
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestResult
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTests
from codemagic.models.xctests.xcresult.xcode_16_xcresult import XcTestStatistic


def test_load_test_results_summary(test_results_summary_dict):
    test_results_summary = XcSummary.from_dict(test_results_summary_dict)

    expected_test_results_summary = XcSummary(
        devices_and_configurations=[
            XcTestPlanConfiguration(
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
                test_plan_configuration=XcConfiguration(
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
        result=XcTestResult.FAILED,
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
    test_results_tests = XcTests.from_dict(test_results_tests_dict)

    expected_test_results_tests = XcTests(
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
        test_nodes=[
            XcTestNode(
                name="banaan",
                node_type=XcTestNodeType.TEST_PLAN,
                result=XcTestResult.FAILED,
                children=[
                    XcTestNode(
                        name="banaanTests",
                        node_type=XcTestNodeType.UNIT_TEST_BUNDLE,
                        result=XcTestResult.FAILED,
                        children=[
                            XcTestNode(
                                name="banaanTests",
                                node_type=XcTestNodeType.TEST_SUITE,
                                result=XcTestResult.FAILED,
                                children=[
                                    XcTestNode(
                                        name="testDisabledExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.PASSED,
                                        duration="0,0011s",
                                        node_identifier="banaanTests/testDisabledExample()",
                                    ),
                                    XcTestNode(
                                        name="testExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.PASSED,
                                        duration="0,00045s",
                                        node_identifier="banaanTests/testExample()",
                                    ),
                                    XcTestNode(
                                        name="testExceptionExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.FAILED,
                                        duration="0,2s",
                                        node_identifier="banaanTests/testExceptionExample()",
                                        children=[
                                            XcTestNode(
                                                name='banaanTests.swift:50: failed: caught error: "badInput"',
                                                node_type=XcTestNodeType.FAILURE_MESSAGE,
                                                result=XcTestResult.FAILED,
                                            ),
                                        ],
                                    ),
                                    XcTestNode(
                                        name="testFailExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.FAILED,
                                        duration="0,002s",
                                        node_identifier="banaanTests/testFailExample()",
                                        children=[
                                            XcTestNode(
                                                name="banaanTests.swift:44: failed - This won't make the cut",
                                                node_type=XcTestNodeType.FAILURE_MESSAGE,
                                                result=XcTestResult.FAILED,
                                            ),
                                        ],
                                    ),
                                    XcTestNode(
                                        name="testPerformanceExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.PASSED,
                                        duration="0,26s",
                                        node_identifier="banaanTests/testPerformanceExample()",
                                    ),
                                    XcTestNode(
                                        name="testSkippedExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.SKIPPED,
                                        duration="0,0052s",
                                        node_identifier="banaanTests/testSkippedExample()",
                                        children=[
                                            XcTestNode(
                                                name="Test skipped - This test is skipped",
                                                node_type=XcTestNodeType.FAILURE_MESSAGE,
                                                result=XcTestResult.SKIPPED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    XcTestNode(
                        name="banaanUITests",
                        node_type=XcTestNodeType.UI_TEST_BUNDLE,
                        result=XcTestResult.FAILED,
                        children=[
                            XcTestNode(
                                name="banaanUITests",
                                node_type=XcTestNodeType.TEST_SUITE,
                                result=XcTestResult.FAILED,
                                children=[
                                    XcTestNode(
                                        name="testUIExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.PASSED,
                                        duration="2s",
                                        node_identifier="banaanUITests/testUIExample()",
                                    ),
                                    XcTestNode(
                                        name="testUIFailExample()",
                                        node_type=XcTestNodeType.TEST_CASE,
                                        result=XcTestResult.FAILED,
                                        duration="3s",
                                        node_identifier="banaanUITests/testUIFailExample()",
                                        children=[
                                            XcTestNode(
                                                name="banaanUITests.swift:40: failed - Bad UI",
                                                node_type=XcTestNodeType.FAILURE_MESSAGE,
                                                result=XcTestResult.FAILED,
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
            XcConfiguration(configuration_id="1", configuration_name="Test Scheme Action"),
        ],
    )

    assert test_results_tests == expected_test_results_tests
