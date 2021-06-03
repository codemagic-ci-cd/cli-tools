import pathlib
from xml.etree import ElementTree

import pytest

from codemagic.models.junit import Error
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuite
from codemagic.models.junit import TestSuites


@pytest.fixture()
def _testsuites() -> TestSuites:
    return TestSuites(
        name='',
        test_suites=[
            TestSuite(
                name='banaanTests',
                tests=5,
                disabled=0,
                errors=1,
                failures=1,
                package='banaanTests',
                skipped=1,
                time=0.31836485862731934,
                timestamp='2020-10-29T15:35:53',
                properties=[
                    Property(name='device_architecture', value='x86_64'),
                    Property(name='device_identifier', value='7C2AC071-3FAE-4370-81D8-079BC87CC391'),
                    Property(name='device_name', value='iPhone 8'),
                    Property(name='device_operating_system', value='13.2.2 (17B102)'),
                    Property(name='device_platform', value='iOS Simulator'),
                    Property(name='ended_time', value='2020-10-29T15:35:53'),
                    Property(name='started_time', value='2020-10-29T15:33:18'),
                    Property(name='title', value='Testing project banaan with scheme banaan'),
                ],
                testcases=[
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
                        assertions=None,
                        status='Failure',
                        time=0.02912592887878418,
                        error=Error(
                            message=(
                                'failed: caught error: "The operation couldn’t be completed. '
                                '(banaanTests.MyErrors error 0.)"'
                            ),
                            type='banaanTests.MyErrors',
                            error_description=(
                                'failed: caught error: "The operation couldn’t be completed. '
                                '(banaanTests.MyErrors error 0.)"\n'
                                'Thrown Error: failed: caught error: '
                                '"The operation couldn’t be completed. (banaanTests.MyErrors error 0.)"'
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
                            message="failed - This won't make the cut",
                            type='Assertion Failure',
                            failure_description=(
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:44 '
                                "failed - This won't make the cut\n"
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
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:34 '
                                'Test skipped - This test is skipped'
                            ),
                        ),
                    ),
                ],
            ),
            TestSuite(
                name='banaanUITests',
                tests=2,
                disabled=0,
                errors=0,
                failures=1,
                package='banaanUITests',
                skipped=0,
                time=4.375350117683411,
                timestamp='2020-10-29T15:35:53',
                properties=[
                    Property(name='device_architecture', value='x86_64'),
                    Property(name='device_identifier', value='7C2AC071-3FAE-4370-81D8-079BC87CC391'),
                    Property(name='device_name', value='iPhone 8'),
                    Property(name='device_operating_system', value='13.2.2 (17B102)'),
                    Property(name='device_platform', value='iOS Simulator'),
                    Property(name='ended_time', value='2020-10-29T15:35:53'),
                    Property(name='started_time', value='2020-10-29T15:33:18'),
                    Property(name='title', value='Testing project banaan with scheme banaan'),
                ],
                testcases=[
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
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2UITests/banaanUITests.swift:40 '
                                'failed - Bad UI\n'
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
                ],
            ),
            TestSuite(
                name='banaanTests',
                tests=5,
                disabled=0,
                errors=1,
                failures=1,
                package='banaanTests',
                skipped=1,
                time=0.35574495792388916,
                timestamp='2020-10-29T15:35:57',
                properties=[
                    Property(name='device_architecture', value='x86_64'),
                    Property(name='device_identifier', value='87895091-1524-455B-A549-12ADED0AD7F0'),
                    Property(name='device_name', value='iPhone 8'),
                    Property(name='device_operating_system', value='14.0 (18A372)'),
                    Property(name='device_platform', value='iOS Simulator'),
                    Property(name='ended_time', value='2020-10-29T15:35:57'),
                    Property(name='started_time', value='2020-10-29T15:33:18'),
                    Property(name='title', value='Testing project banaan with scheme banaan'),
                ],
                testcases=[
                    TestCase(
                        classname='banaanTests',
                        name='testExample()',
                        assertions=None,
                        status='Success',
                        time=0.009827971458435059,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname='banaanTests',
                        name='testExceptionExample()',
                        assertions=None,
                        status='Failure',
                        time=0.08241903781890869,
                        error=Error(
                            message='failed: caught error: "badInput"',
                            type='banaanTests.MyErrors',
                            error_description=(
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:50 '
                                'failed: caught error: "badInput"\n'
                                'Thrown Error at banaanTests.swift:50: failed: caught error: "badInput"'
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
                        time=0.0036939382553100586,
                        error=None,
                        failure=Failure(
                            message="failed - This won't make the cut",
                            type='Assertion Failure',
                            failure_description=(
                                '/Users/priit/nevercode/banaan-ios/ios-test2/'
                                "ios-test2Tests/banaanTests.swift:44 failed - This won't make the cut\n"
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
                        time=0.2537109851837158,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname='banaanTests',
                        name='testSkippedExample()',
                        assertions=None,
                        status='Skipped',
                        time=0.006093025207519531,
                        error=None,
                        failure=None,
                        skipped=Skipped(
                            message=(
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2Tests/banaanTests.swift:34 '
                                'Test skipped - This test is skipped'
                            ),
                        ),
                    ),
                ],
            ),
            TestSuite(
                name='banaanUITests',
                tests=2,
                disabled=0,
                errors=0,
                failures=1,
                package='banaanUITests',
                skipped=0,
                time=5.046915054321289,
                timestamp='2020-10-29T15:35:57',
                properties=[
                    Property(name='device_architecture', value='x86_64'),
                    Property(name='device_identifier', value='87895091-1524-455B-A549-12ADED0AD7F0'),
                    Property(name='device_name', value='iPhone 8'),
                    Property(name='device_operating_system', value='14.0 (18A372)'),
                    Property(name='device_platform', value='iOS Simulator'),
                    Property(name='ended_time', value='2020-10-29T15:35:57'),
                    Property(name='started_time', value='2020-10-29T15:33:18'),
                    Property(name='title', value='Testing project banaan with scheme banaan'),
                ],
                testcases=[
                    TestCase(
                        classname='banaanUITests',
                        name='testUIExample()',
                        assertions=None,
                        status='Success',
                        time=1.7833280563354492,
                        error=None,
                        failure=None,
                        skipped=None,
                    ),
                    TestCase(
                        classname='banaanUITests',
                        name='testUIFailExample()',
                        assertions=None,
                        status='Failure',
                        time=3.26358699798584,
                        error=None,
                        failure=Failure(
                            message='failed - Bad UI',
                            type='Assertion Failure',
                            failure_description=(
                                '/Users/priit/nevercode/banaan-ios/ios-test2/ios-test2UITests/banaanUITests.swift:40 '
                                'failed - Bad UI\n'
                                'Start Test at 2020-10-29 15:34:42.837\n'
                                'Set Up\n'
                                '    Open io.codemagic.banaan\n'
                                '        Launch io.codemagic.banaan\n'
                                '            Terminate io.codemagic.banaan:57051\n'
                                '            Setting up automation session\n'
                                '            Wait for io.codemagic.banaan to idle\n'
                                'Assertion Failure at banaanUITests.swift:40: failed - Bad UI\n'
                                'Tear Down'
                            ),
                        ),
                        skipped=None,
                    ),
                ],
            ),
        ],
    )


@pytest.fixture()
def expected_xml_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / 'mocks' / 'testsuite.xml'


def _assert_elements_are_equal(el_1, el_2):
    assert el_1.tag == el_2.tag
    assert el_1.text == el_2.text
    assert el_1.tail == el_2.tail
    assert el_1.attrib == el_2.attrib
    assert len(el_1) == len(el_2)
    return all(_assert_elements_are_equal(c1, c2) for c1, c2 in zip(el_1, el_2))


def test_xml(temp_dir, _testsuites, expected_xml_path):
    xml_path = temp_dir / 'testsuite.xml'
    _testsuites.save_xml(xml_path)
    generated_xml = ElementTree.parse(xml_path)
    expected_xml = ElementTree.parse(expected_xml_path)
    _assert_elements_are_equal(generated_xml.getroot(), expected_xml.getroot())
