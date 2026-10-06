from __future__ import annotations

import pathlib
import re
from datetime import datetime
from datetime import timedelta
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from codemagic.models.junit import Error
from codemagic.models.junit import Property
from codemagic.models.junit import Skipped
from codemagic.models.junit import TestCase
from codemagic.models.junit import TestSuite
from codemagic.models.junit import TestSuites

from .xcresult import XcDevice
from .xcresult import XcSummary
from .xcresult import XcTestNode
from .xcresult import XcTestNodeType
from .xcresult import XcTestResult
from .xcresult import XcTests
from .xcresulttool import XcResultTool


class XcResultConverter:
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

    @classmethod
    def _iter_nodes(
        cls,
        root_node: XcTestNode,
        node_type: XcTestNodeType,
        skip_subtree_node_type: Optional[XcTestNodeType] = None,
    ) -> Iterator[XcTestNode]:
        if root_node.node_type is node_type:
            yield root_node
        elif root_node.node_type is not skip_subtree_node_type:
            for child in root_node.children:
                yield from cls._iter_nodes(child, node_type, skip_subtree_node_type)

    @classmethod
    def _get_run_destination(cls, root_node: XcTestNode) -> Optional[XcDevice]:
        # TODO: support multiple run destinations
        #  As a first iteration only the first test destination is used

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

        failure_messages_nodes = cls._iter_nodes(
            xc_test_case,
            XcTestNodeType.FAILURE_MESSAGE,
            skip_subtree_node_type=XcTestNodeType.EXPECTED_FAILURE,
        )
        unexpected_failure_message_nodes = (
            node for node in failure_messages_nodes if node.result is not XcTestResult.EXPECTED_FAILURE
        )
        failure_messages = [node.name for node in unexpected_failure_message_nodes if node.name]
        return Error(
            message=failure_messages[0] if failure_messages else "",
            type="Error" if any("caught error" in m for m in failure_messages) else "Failure",
            error_description="\n".join(failure_messages) if len(failure_messages) > 1 else None,
        )

    @classmethod
    def _get_test_case_skipped(cls, xc_test_case: XcTestNode) -> Optional[Skipped]:
        if xc_test_case.result is not XcTestResult.SKIPPED:
            return None

        # Schema 0.1.0 / Xcode 16: skip reason is a Failure Message child with result Skipped.
        failure_messages_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.FAILURE_MESSAGE)
        skipped_message_nodes = (node for node in failure_messages_nodes if node.result is XcTestResult.SKIPPED)
        skipped_messages = [node.name for node in skipped_message_nodes if node.name]

        # Schema 0.2.0+ / Xcode 27: skip reason is a Skip Message child.
        skip_message_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.SKIP_MESSAGE)
        skipped_messages.extend(node.name for node in skip_message_nodes if node.name)

        unique_skipped_messages = dict.fromkeys(skipped_messages)
        return Skipped(message="\n".join(unique_skipped_messages))

    @classmethod
    def _get_test_case_system_out(cls, xc_test_case: XcTestNode) -> Optional[str]:
        expected_failure_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.EXPECTED_FAILURE)
        reasons = [node.name for node in expected_failure_nodes if node.name]

        failure_messages_nodes = cls._iter_nodes(xc_test_case, XcTestNodeType.FAILURE_MESSAGE)
        expected_failure_message_nodes = (
            node for node in failure_messages_nodes if node.result is XcTestResult.EXPECTED_FAILURE
        )
        reasons.extend(node.name for node in expected_failure_message_nodes if node.name)

        if not reasons:
            return None
        return "\n".join(dict.fromkeys(reasons))

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
            system_out=cls._get_test_case_system_out(xc_test_case),
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
