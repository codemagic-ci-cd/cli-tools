from __future__ import annotations

import pathlib
import re
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from codemagic.models.junit import Error
from codemagic.models.junit import Failure
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuite
from codemagic.models.junit import TestSuites

from .xcresult import ActionDeviceRecord
from .xcresult import ActionRecord
from .xcresult import ActionsInvocationRecord
from .xcresult import ActionTestableSummary
from .xcresult import ActionTestMetadata
from .xcresult import XcDevice
from .xcresult import XcSummary
from .xcresult import XcTestNode
from .xcresult import XcTestNodeType
from .xcresult import XcTestResult
from .xcresult import XcTests
from .xcresulttool import XcResultTool


class XcResultConverter(ABC):
    def __new__(cls, *args, **kwargs):
        if cls is XcResultConverter:
            if XcResultTool.is_legacy():
                cls = LegacyXcResultConverter
            else:
                cls = Xcode16XcResultConverter
        return object.__new__(cls)

    def __init__(self, xcresult: pathlib.Path):
        self.xcresult = xcresult

    @classmethod
    def _timestamp(cls, date: Union[datetime, float, int]) -> str:
        if isinstance(date, (float, int)):
            date = datetime.fromtimestamp(date)
        return date.strftime("%Y-%m-%dT%H:%M:%S")

    @classmethod
    def xcresult_to_junit(cls, xcresult: pathlib.Path) -> TestSuites:
        return cls(xcresult).convert()

    @abstractmethod
    def convert(self) -> TestSuites:
        raise NotImplementedError()


class LegacyXcResultConverter(XcResultConverter):
    @classmethod
    def _get_test_case_error(cls, test: ActionTestMetadata) -> Optional[Error]:
        if not test.is_error():
            return None
        return Error(
            message=test.get_error_message(),
            type=test.get_error_type(),
            error_description=test.get_failure_description(),
        )

    @classmethod
    def _get_test_case_failure(cls, test: ActionTestMetadata) -> Optional[Failure]:
        if not test.is_failure():
            return None
        return Failure(
            message=test.get_failure_message(),
            type=test.get_failure_type(),
            failure_description=test.get_failure_description(),
        )

    @classmethod
    def _get_test_case_skipped(cls, test: ActionTestMetadata) -> Optional[Skipped]:
        if not test.is_skipped():
            return None
        return Skipped(message=test.get_skipped_message())

    @classmethod
    def _get_test_case(cls, test: ActionTestMetadata) -> TestCase:
        return TestCase(
            name=test.get_method_name(),
            classname=test.get_classname(),
            error=cls._get_test_case_error(test),
            failure=cls._get_test_case_failure(test),
            time=test.duration,
            status=test.test_status,
            skipped=cls._get_test_case_skipped(test),
        )

    @classmethod
    def _get_test_suite_run_destination(cls, action: ActionRecord) -> Optional[ActionDeviceRecord]:
        if action.run_destination and action.run_destination.target_device_record:
            return action.run_destination.target_device_record
        return None

    @classmethod
    def _get_test_suite_properties(cls, action: ActionRecord) -> List[Property]:
        properties: List[Property] = [
            Property(name="started_time", value=cls._timestamp(action.started_time)),
            Property(name="ended_time", value=cls._timestamp(action.ended_time)),
        ]
        if action.title:
            properties.append(Property(name="title", value=action.title))

        device = cls._get_test_suite_run_destination(action)
        if device:
            properties.extend(
                [
                    Property(name="device_name", value=device.model_name),
                    Property(name="device_architecture", value=device.native_architecture),
                    Property(name="device_identifier", value=device.identifier),
                    Property(name="device_operating_system", value=device.operating_system_version_with_build_number),
                    Property(name="device_platform", value=device.platform_record.user_description),
                ],
            )
        return sorted(properties, key=lambda p: p.name)

    @classmethod
    def _get_test_suite_name(cls, action: ActionRecord, testable_summary: ActionTestableSummary):
        name = testable_summary.name or ""
        device_info = ""

        device = cls._get_test_suite_run_destination(action)
        if device:
            platform_name = device.platform_record.user_description
            platform = re.sub("simulator", "", platform_name, flags=re.IGNORECASE).strip()
            device_info = f"{platform} {device.operating_system_version} {device.model_name}"

        if name and device_info:
            return f"{name} [{device_info}]"
        return name or device_info

    @classmethod
    def _get_test_suite(cls, action: ActionRecord, testable_summary: ActionTestableSummary) -> TestSuite:
        tests = testable_summary.get_tests()
        return TestSuite(
            name=cls._get_test_suite_name(action, testable_summary),
            tests=len(tests),
            disabled=sum(t.is_disabled() for t in tests),
            errors=sum(t.is_error() for t in tests),
            failures=sum(t.is_failure() for t in tests),
            package=testable_summary.name,
            skipped=sum(t.is_skipped() for t in tests),
            time=sum((test.duration or 0) for test in tests),
            timestamp=cls._timestamp(action.ended_time),
            testcases=[cls._get_test_case(test) for test in tests],
            properties=cls._get_test_suite_properties(action),
        )

    @classmethod
    def _get_action_test_suites(cls, action: ActionRecord) -> Iterator[TestSuite]:
        run_summaries = action.action_result.action_test_plan_run_summaries
        test_summaries = run_summaries.summaries if run_summaries else []
        for test_summary in test_summaries:
            for testable_summary in test_summary.testable_summaries:
                yield cls._get_test_suite(action, testable_summary)

    @classmethod
    def actions_invocation_record_to_junit(cls, actions_invocation_record: ActionsInvocationRecord) -> TestSuites:
        test_suites: List[TestSuite] = []
        for action in actions_invocation_record.actions:
            test_suites.extend(cls._get_action_test_suites(action))
        return TestSuites(name="", test_suites=test_suites)

    def convert(self) -> TestSuites:
        actions_invocation_record = ActionsInvocationRecord.from_xcresult(self.xcresult)
        return self.actions_invocation_record_to_junit(actions_invocation_record)


class Xcode16XcResultConverter(XcResultConverter):
    @classmethod
    def _iter_nodes(cls, root_node: XcTestNode, node_type: XcTestNodeType) -> Iterator[XcTestNode]:
        if root_node.node_type is node_type:
            yield root_node
        else:
            for child in root_node.children:
                yield from cls._iter_nodes(child, node_type)

    @classmethod
    def _get_run_destination(cls, root_node: XcTestNode) -> Optional[XcDevice]:
        # TODO: support multiple run destinations
        #  As a first iteration only one test destination is supported as in legacy mode

        parent: Union[XcTests, XcTestNode] = root_node
        while isinstance(parent, XcTestNode):
            parent = parent.parent

        tests = cast(XcTests, parent)
        if not tests.devices:
            return None
        return tests.devices[0]

    @classmethod
    def _get_test_suite_name(cls, xc_test_suite: XcTestNode) -> str:
        name = xc_test_suite.name or ""

        device = cls._get_run_destination(xc_test_suite)
        if device and device.platform is not None:
            platform = re.sub("simulator", "", device.platform, flags=re.IGNORECASE).strip()
            device_info = f"{platform} {device.os_version} {device.model_name}"
        elif device:
            device_info = f"{device.os_version} {device.model_name}"
        else:
            device_info = ""

        if name and device_info:
            return f"{name} [{device_info}]"
        return name or device_info

    @classmethod
    def _get_test_case_error(cls, xc_test_case: XcTestNode) -> Optional[Error]:
        if xc_test_case.result is not XcTestResult.FAILED:
            return None

        failure_messages_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.FAILURE_MESSAGE)
        failure_messages = [node.name for node in failure_messages_nodes if node.name]
        return Error(
            message=failure_messages[0] if failure_messages else "",
            type="Error" if any("caught error" in m for m in failure_messages) else "Failure",
            error_description="\n".join(failure_messages) if len(failure_messages) > 1 else None,
        )

    @classmethod
    def _get_test_case_skipped(cls, xc_test_case: XcTestNode) -> Optional[Skipped]:
        if xc_test_case.result is not XcTestResult.SKIPPED:
            return None

        failure_messages_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.FAILURE_MESSAGE)
        skipped_message_nodes = (node for node in failure_messages_nodes if node.result is XcTestResult.SKIPPED)
        skipped_messages = [node.name for node in skipped_message_nodes if node.name]

        return Skipped(message="\n".join(skipped_messages))

    @classmethod
    def parse_xcresult_test_node_duration_value(cls, xc_duration: str) -> float:
        duration = timedelta()

        try:
            for part in xc_duration.split():
                part_value = float(part[:-1].replace(",", "."))
                if part.endswith("s"):
                    duration += timedelta(seconds=part_value)
                elif part.endswith("m"):
                    duration += timedelta(minutes=part_value)
                else:
                    raise ValueError("Unknown duration unit")
        except ValueError as ve:
            raise ValueError("Invalid duration", xc_duration) from ve

        return duration.total_seconds()

    @classmethod
    def _get_test_node_duration(cls, xc_test_case: XcTestNode) -> float:
        if not xc_test_case.duration:
            return 0.0

        return cls.parse_xcresult_test_node_duration_value(xc_test_case.duration)

    @classmethod
    def _get_test_case(cls, xc_test_case: XcTestNode, xc_test_suite: XcTestNode) -> TestCase:
        if xc_test_case.name:
            method_name = xc_test_case.name
        elif xc_test_case.node_identifier:
            method_name = xc_test_case.node_identifier.split("/")[-1]
        else:
            method_name = ""

        if xc_test_case.node_identifier:
            classname = xc_test_case.node_identifier.split("/", maxsplit=1)[0]
        elif xc_test_suite.name:
            classname = xc_test_suite.name
        else:
            classname = ""

        return TestCase(
            name=method_name,
            classname=classname,
            error=cls._get_test_case_error(xc_test_case),
            time=cls._get_test_node_duration(xc_test_case),
            status=xc_test_case.result.value if xc_test_case.result else None,
            skipped=cls._get_test_case_skipped(xc_test_case),
        )

    @classmethod
    def _get_test_suite_properties(
        cls,
        xc_test_suite: XcTestNode,
        xc_test_result_summary: XcSummary,
    ) -> List[Property]:
        device = cls._get_run_destination(xc_test_suite)

        properties: List[Property] = [Property(name="title", value=xc_test_suite.name)]
        if xc_test_result_summary.start_time:
            properties.append(Property(name="started_time", value=cls._timestamp(xc_test_result_summary.start_time)))
        if xc_test_result_summary.finish_time:
            properties.append(Property(name="ended_time", value=cls._timestamp(xc_test_result_summary.finish_time)))
        if device and device.model_name:
            properties.append(Property(name="device_name", value=device.model_name))
        if device and device.architecture:
            properties.append(Property(name="device_architecture", value=device.architecture))
        if device and device.device_id:
            properties.append(Property(name="device_identifier", value=device.device_id))
        if device and device.os_version:
            properties.append(Property(name="device_operating_system", value=device.os_version))
        if device and device.platform:
            properties.append(Property(name="device_platform", value=device.platform))

        return sorted(properties, key=lambda p: p.name)

    @classmethod
    def _get_test_suite(cls, xc_test_suite: XcTestNode, xc_test_result_summary: XcSummary) -> TestSuite:
        xc_test_cases = list(cls._iter_nodes(xc_test_suite, XcTestNodeType.TEST_CASE))

        timestamp = None
        if xc_test_result_summary.finish_time:
            timestamp = cls._timestamp(xc_test_result_summary.finish_time)

        return TestSuite(
            name=cls._get_test_suite_name(xc_test_suite),
            tests=len(xc_test_cases),
            disabled=0,  # Disabled tests are completely excluded from reports
            errors=sum(1 for xc_test_case in xc_test_cases if xc_test_case.result is XcTestResult.FAILED),
            failures=None,  # Xcode doesn't differentiate errors from failures, consider everything as error
            package=xc_test_suite.name,
            skipped=sum(1 for xc_test_case in xc_test_cases if xc_test_case.result is XcTestResult.SKIPPED),
            time=sum(cls._get_test_node_duration(xc_test_case) for xc_test_case in xc_test_cases),
            timestamp=timestamp,
            testcases=[cls._get_test_case(xc_test_case, xc_test_suite) for xc_test_case in xc_test_cases],
            properties=cls._get_test_suite_properties(xc_test_suite, xc_test_result_summary),
        )

    def convert(self) -> TestSuites:
        tests_output = XcResultTool.get_test_report_tests(self.xcresult)
        summary_output = XcResultTool.get_test_report_summary(self.xcresult)

        xc_tests = XcTests.from_dict(tests_output)
        xc_summary = XcSummary.from_dict(summary_output)

        test_suites = [
            self._get_test_suite(xc_test_suite_node, xc_summary)
            for xc_test_node in xc_tests.test_nodes
            for xc_test_suite_node in self._iter_nodes(xc_test_node, XcTestNodeType.TEST_SUITE)
        ]

        return TestSuites(
            name=xc_summary.title,
            test_suites=test_suites,
        )
