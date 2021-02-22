from __future__ import annotations

import pathlib
import re
from datetime import datetime
from typing import Iterator
from typing import List
from typing import Optional

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


class XcResultConverter:

    @classmethod
    def _timestamp(cls, date: datetime) -> str:
        return date.strftime('%Y-%m-%dT%H:%M:%S')

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
            Property(name='started_time', value=cls._timestamp(action.started_time)),
            Property(name='ended_time', value=cls._timestamp(action.ended_time)),
        ]
        if action.title:
            properties.append(Property(name='title', value=action.title))

        device = cls._get_test_suite_run_destination(action)
        if device:
            properties.extend([
                Property(name='device_name', value=device.model_name),
                Property(name='device_architecture', value=device.native_architecture),
                Property(name='device_identifier', value=device.identifier),
                Property(name='device_operating_system', value=device.operating_system_version_with_build_number),
                Property(name='device_platform', value=device.platform_record.user_description),
            ])
        return sorted(properties, key=lambda p: p.name)

    @classmethod
    def _get_test_suite_name(cls, action: ActionRecord, testable_summary: ActionTestableSummary):
        name = testable_summary.name or ''
        device_info = ''

        device = cls._get_test_suite_run_destination(action)
        if device:
            platform_name = device.platform_record.user_description
            platform = re.sub('simulator', '', platform_name, flags=re.IGNORECASE).strip()
            device_info = f'{platform} {device.operating_system_version} {device.model_name}'

        if name and device_info:
            return f'{name} [{device_info}]'
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
        return TestSuites(name='', test_suites=test_suites)

    @classmethod
    def xcresult_to_junit(cls, xcresult: pathlib.Path) -> TestSuites:
        actions_invocation_record = ActionsInvocationRecord.from_xcresult(xcresult)
        return cls.actions_invocation_record_to_junit(actions_invocation_record)
