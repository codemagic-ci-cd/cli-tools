"""
This module describes explicitly Xcode test result (xcresult)
JSON bundle as Python classes. Result Bundle Format Description
is created according to the description from
`xcrun xcresulttool formatDescription get`.
"""

from __future__ import annotations

import pathlib
from abc import ABCMeta
from datetime import datetime
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.models.xctests.xcresulttool import XcResultTool


class _BaseAbstractRecord(metaclass=ABCMeta):
    def __init__(self, data: Dict, xcresult: pathlib.Path):
        self._data = data
        self._xcresult = xcresult
        self.type = data["_type"]["_name"]


T = TypeVar("T", bool, float, int, str)
R = TypeVar("R", bound=_BaseAbstractRecord)
SchemaSerializable = Union[bool, float, int, str]


@lru_cache()
def _get_cached_object_from_bundle(xcresult: pathlib.Path, object_id: Optional[str] = None) -> Dict[str, Any]:
    if object_id is None:
        return XcResultTool.get_bundle(xcresult)
    else:
        return XcResultTool.get_object(xcresult, object_id)


class _AbstractRecord(_BaseAbstractRecord, metaclass=ABCMeta):
    def _get_primitive_value(self, key: str, type_name: str, default: T) -> T:
        try:
            value_container = self._data[key]
        except KeyError:
            return default
        given_type = value_container["_type"]["_name"]
        assert given_type == type_name, f"Expected type {type_name}, but was {given_type}"
        value: T = default.__class__(value_container["_value"])
        return value

    def _schema_serializable_value(self, key: str) -> SchemaSerializable:
        getters: Dict[Type[SchemaSerializable], Callable[[str], SchemaSerializable]] = {
            bool: self._bool_value,
            float: self._float_value,
            int: self._int_value,
            str: self._str_value,
        }
        for _type, getter in getters.items():
            try:
                return getter(key)
            except AssertionError:
                continue

        value_container = self._data[key]
        given_type = value_container["_type"]["_name"]
        raise AssertionError(f"Expected types Bool, Double, Int, String, but was {given_type}")

    def _bool_value(self, key: str, *, default: bool = False) -> bool:
        return self._get_primitive_value(key, "Bool", default)

    def _optional_bool_value(self, key: str) -> Optional[bool]:
        if key in self._data:
            return self._bool_value(key)
        return None

    def _date_value(self, key: str) -> datetime:
        value_container = self._data[key]
        assert value_container["_type"]["_name"] == "Date"
        value: str = value_container["_value"]
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")

    def _optional_date_value(self, key: str) -> Optional[datetime]:
        if key in self._data:
            return self._date_value(key)
        return None

    def _float_value(self, key: str, default: float = 0.0) -> float:
        return self._get_primitive_value(key, "Double", default)

    def _optional_float_value(self, key: str) -> Optional[float]:
        if key in self._data:
            return self._float_value(key)
        return None

    def _int_value(self, key: str, default: int = 0) -> int:
        return self._get_primitive_value(key, "Int", default)

    def _optional_int_value(self, key: str) -> Optional[int]:
        if key in self._data:
            return self._int_value(key)
        return None

    def _str_value(self, key: str, default: str = "") -> str:
        return self._get_primitive_value(key, "String", default)

    def _optional_str_value(self, key: str) -> Optional[str]:
        if key in self._data:
            return self._str_value(key)
        return None

    def _get_primitive_array_values(self, key: str, type_name: str, _type: Type[T]) -> List[T]:
        try:
            values_container = self._data[key]
        except KeyError:
            return []

        assert values_container["_type"]["_name"] == "Array"
        values: List[Dict] = values_container["_values"]
        typed_values: List[T] = []
        for value_container in values:
            given_type = value_container["_type"]["_name"]
            assert given_type == type_name, f"Expected type {type_name}, but was {given_type}"
            value: T = value_container["_value"]
            typed_values.append(value)

        return typed_values

    def _array_str_values(self, key: str) -> List[str]:
        return self._get_primitive_array_values(key, "String", str)

    def _array_float_values(self, key: str) -> List[float]:
        return self._get_primitive_array_values(key, "Double", float)

    def _array_values(self, key: str, *member_types: Type[R]) -> List[R]:
        try:
            values_container = self._data[key]
        except KeyError:
            return []
        assert values_container["_type"]["_name"] == "Array"
        values: List[Dict] = values_container["_values"]
        typed_values: List[R] = []
        for value in values:
            given_type = value["_type"]["_name"]
            for member_type in member_types:
                if given_type == member_type.__name__:
                    member: R = member_type(value, self._xcresult)
                    typed_values.append(member)
                    break
            else:
                expected_types = ", ".join(t.__name__ for t in member_types)
                raise AssertionError(f"Expected types {expected_types}, but was {given_type}")

        return typed_values

    def _object_value(self, key: str, object_type: Type[R]) -> R:
        value = self._data[key]
        given_type = value["_type"]["_name"]
        assert given_type == object_type.__name__, f"Expected type {object_type.__name__}, but was {given_type}"
        return object_type(value, self._xcresult)

    def _optional_object_value(self, key: str, object_type: Type[R]) -> Optional[R]:
        if key in self._data:
            return self._object_value(key, object_type)
        return None

    def _get_referenced_object(self, reference: Optional[Reference], *object_types: Type[R]) -> Optional[R]:
        if reference is None:
            return None

        value = _get_cached_object_from_bundle(self._xcresult, object_id=reference.id)
        given_type = value["_type"]["_name"]

        for object_type in object_types:
            if given_type == object_type.__name__:
                return object_type(value, self._xcresult)

        expected_types = ", ".join(t.__name__ for t in object_types)
        raise AssertionError(f"Expected types {expected_types}, but was {given_type}")


class _ActionAbstractTestSummary(_AbstractRecord, metaclass=ABCMeta):
    """
    - ActionAbstractTestSummary
      * Kind: object
      * Properties:
        + name: String?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.name: Optional[str] = self._optional_str_value("name")


class ActionDeviceRecord(_AbstractRecord):
    """
    - ActionDeviceRecord
      * Kind: object
      * Properties:
        + name: String
        + isConcreteDevice: Bool
        + operatingSystemVersion: String
        + operatingSystemVersionWithBuildNumber: String
        + nativeArchitecture: String
        + modelName: String
        + modelCode: String
        + modelUTI: String
        + identifier: String
        + isWireless: Bool
        + cpuKind: String
        + cpuCount: Int?
        + cpuSpeedInMHz: Int?
        + busSpeedInMHz: Int?
        + ramSizeInMegabytes: Int?
        + physicalCPUCoresPerPackage: Int?
        + logicalCPUCoresPerPackage: Int?
        + platformRecord: ActionPlatformRecord
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.name: str = self._str_value("name")
        self.is_concrete_device: bool = self._bool_value("isConcreteDevice")
        self.operating_system_version: str = self._str_value("operatingSystemVersion")
        self.operating_system_version_with_build_number: str = self._str_value("operatingSystemVersionWithBuildNumber")
        self.native_architecture: str = self._str_value("nativeArchitecture")
        self.model_name: str = self._str_value("modelName")
        self.model_code: str = self._str_value("modelCode")
        self.model_uti: str = self._str_value("modelUTI")
        self.identifier: str = self._str_value("identifier")
        self.is_wireless: bool = self._bool_value("isWireless")
        self.cpu_kind: str = self._str_value("cpuKind")
        self.cpu_count: Optional[int] = self._optional_int_value("cpuCount")
        self.cpu_speed_in_mhz: Optional[int] = self._optional_int_value("cpuSpeedInMHz")
        self.bus_speed_in_mhz: Optional[int] = self._optional_int_value("busSpeedInMHz")
        self.ram_size_in_megabytes: Optional[int] = self._optional_int_value("ramSizeInMegabytes")
        self.physical_cpu_cores_per_package: Optional[int] = self._optional_int_value("physicalCPUCoresPerPackage")
        self.logical_cpu_cores_per_package: Optional[int] = self._optional_int_value("logicalCPUCoresPerPackage")
        self.platform_record: ActionPlatformRecord = self._object_value("platformRecord", ActionPlatformRecord)


class ActionPlatformRecord(_AbstractRecord):
    """
    - ActionPlatformRecord
      * Kind: object
      * Properties:
        + identifier: String
        + userDescription: String
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.identifier: str = self._str_value("identifier")
        self.user_description: str = self._str_value("userDescription")


class ActionRecord(_AbstractRecord):
    """
    - ActionRecord
      * Kind: object
      * Properties:
        + schemeCommandName: String
        + schemeTaskName: String
        + title: String?
        + startedTime: Date
        + endedTime: Date
        + runDestination: ActionRunDestinationRecord
        + buildResult: ActionResult
        + actionResult: ActionResult
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.scheme_command_name: str = self._str_value("schemeCommandName")
        self.scheme_task_name: str = self._str_value("schemeTaskName")
        self.title: Optional[str] = self._optional_str_value("title")
        self.started_time: datetime = self._date_value("startedTime")
        self.ended_time: datetime = self._date_value("endedTime")
        self.run_destination: ActionRunDestinationRecord = self._object_value(
            "runDestination",
            ActionRunDestinationRecord,
        )
        self.build_result: ActionResult = self._object_value("buildResult", ActionResult)
        self.action_result: ActionResult = self._object_value("actionResult", ActionResult)


class ActionResult(_AbstractRecord):
    """
    - ActionResult
      * Kind: object
      * Properties:
        + resultName: String
        + status: String
        + metrics: ResultMetrics
        + issues: ResultIssueSummaries
        + coverage: CodeCoverageInfo
        + timelineRef: Reference?
        + logRef: Reference?
        + testsRef: Reference?
        + diagnosticsRef: Reference?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.result_name: str = self._str_value("resultName")
        self.status: str = self._str_value("status")
        self.metrics: ResultMetrics = self._object_value("metrics", ResultMetrics)
        self.issues: ResultIssueSummaries = self._object_value("issues", ResultIssueSummaries)
        self.coverage: CodeCoverageInfo = self._object_value("coverage", CodeCoverageInfo)
        self.timeline_ref: Optional[Reference] = self._optional_object_value("timelineRef", Reference)
        self.log_ref: Optional[Reference] = self._optional_object_value("logRef", Reference)
        self.tests_ref: Optional[Reference] = self._optional_object_value("testsRef", Reference)
        self.diagnostics_ref: Optional[Reference] = self._optional_object_value("diagnosticsRef", Reference)

    @property
    def action_test_plan_run_summaries(self) -> Optional[ActionTestPlanRunSummaries]:
        return self._get_referenced_object(self.tests_ref, ActionTestPlanRunSummaries)


class ActionRunDestinationRecord(_AbstractRecord):
    """
    - ActionRunDestinationRecord
      * Kind: object
      * Properties:
        + displayName: String
        + targetArchitecture: String
        + targetDeviceRecord: ActionDeviceRecord
        + localComputerRecord: ActionDeviceRecord
        + targetSDKRecord: ActionSDKRecord
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.display_name: str = self._str_value("displayName")
        self.target_architecture: str = self._str_value("targetArchitecture")
        self.target_device_record: ActionDeviceRecord = self._object_value("targetDeviceRecord", ActionDeviceRecord)
        self.local_computer_record: ActionDeviceRecord = self._object_value("localComputerRecord", ActionDeviceRecord)
        self.target_sdk_record: ActionSDKRecord = self._object_value("targetSDKRecord", ActionSDKRecord)


class ActionSDKRecord(_AbstractRecord):
    """
    - ActionSDKRecord
      * Kind: object
      * Properties:
        + name: String
        + identifier: String
        + operatingSystemVersion: String
        + isInternal: Bool
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.name: str = self._str_value("name")
        self.identifier: str = self._str_value("identifier")
        self.operating_system_version: str = self._str_value("operatingSystemVersion")
        self.is_internal: bool = self._bool_value("isInternal")


class ActionTestActivitySummary(_AbstractRecord):
    """
    - ActionTestActivitySummary
      * Kind: object
      * Properties:
        + title: String
        + activityType: String
        + uuid: String
        + start: Date?
        + finish: Date?
        + attachments: [ActionTestAttachment]
        + subactivities: [ActionTestActivitySummary]
        + failureSummaryIDs: [String]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.title: str = self._str_value("title")
        self.activity_type: str = self._str_value("activityType")
        self.uuid: str = self._str_value("uuid")
        self.start: Optional[datetime] = self._optional_date_value("start")
        self.finish: Optional[datetime] = self._optional_date_value("finish")
        self.attachments: List[ActionTestAttachment] = self._array_values("attachments", ActionTestAttachment)
        self.subactivities: List[ActionTestActivitySummary] = self._array_values(
            "subactivities",
            ActionTestActivitySummary,
        )
        self.failure_summary_ids: List[str] = self._array_str_values("failureSummaryIDs")

    def get_description(self) -> str:
        lines = []
        if self.title:
            lines.append(self.title)
        for subactivity in self.subactivities:
            description = subactivity.get_description()
            if description:
                lines.extend(f"    {line}" for line in description.splitlines())
        return "\n".join(lines)


class ActionTestAttachment(_AbstractRecord):
    """
    - ActionTestAttachment
      * Kind: object
      * Properties:
        + uniformTypeIdentifier: String
        + name: String?
        + timestamp: Date?
        + userInfo: SortedKeyValueArray?
        + lifetime: String
        + inActivityIdentifier: Int
        + filename: String?
        + payloadRef: Reference?
        + payloadSize: Int
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.uniform_type_identifier: str = self._str_value("uniformTypeIdentifier")
        self.name: Optional[str] = self._optional_str_value("name")
        self.timestamp: Optional[datetime] = self._optional_date_value("timestamp")
        self.user_info: Optional[SortedKeyValueArray] = self._optional_object_value("userInfo", SortedKeyValueArray)
        self.lifetime: str = self._str_value("lifetime")
        self.in_activity_identifier: int = self._int_value("inActivityIdentifier")
        self.filename: Optional[str] = self._optional_str_value("filename")
        self.payload_ref: Optional[Reference] = self._optional_object_value("payloadRef", Reference)
        self.payload_size: int = self._int_value("payloadSize")


class ActionTestFailureSummary(_AbstractRecord):
    """
    - ActionTestFailureSummary
      * Kind: object
      * Properties:
        + message: String?
        + fileName: String
        + lineNumber: Int
        + isPerformanceFailure: Bool
        + uuid: String
        + issueType: String?
        + detailedDescription: String?
        + attachments: [ActionTestAttachment]
        + associatedError: TestAssociatedError?
        + sourceCodeContext: SourceCodeContext?
        + timestamp: Date?
        + isTopLevelFailure: Bool
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.message: Optional[str] = self._optional_str_value("message")
        self.file_name: str = self._str_value("fileName")
        self.line_number: int = self._int_value("lineNumber")
        self.is_performance_failure: bool = self._bool_value("isPerformanceFailure")
        self.uuid: str = self._str_value("uuid")
        self.issue_type: Optional[str] = self._optional_str_value("issueType")
        self.detailed_description: Optional[str] = self._optional_str_value("detailedDescription")
        self.attachments: List[ActionTestAttachment] = self._array_values("attachments", ActionTestAttachment)
        self.associated_error: Optional[TestAssociatedError] = self._optional_object_value(
            "associatedError",
            TestAssociatedError,
        )
        self.source_code_context: Optional[SourceCodeContext] = self._optional_object_value(
            "sourceCodeContext",
            SourceCodeContext,
        )
        self.timestamp: Optional[datetime] = self._optional_date_value("timestamp")
        self.is_top_level_failure: bool = self._bool_value("isTopLevelFailure")

    def get_description(self) -> str:
        line_number = self.line_number
        file_name = self.file_name
        if self.source_code_context and self.source_code_context.location:
            if self.source_code_context.location.line_number:
                line_number = self.source_code_context.location.line_number
            if self.source_code_context.location.file_path:
                file_name = self.source_code_context.location.file_path

        if file_name and line_number:
            prefix = f"{self.file_name}:{self.line_number} "
        else:
            prefix = ""

        message = self.detailed_description or self.message or self.issue_type or ""

        return f"{prefix}{message}"


class ActionTestNoticeSummary(_AbstractRecord):
    """
    - ActionTestNoticeSummary
      * Kind: object
      * Properties:
        + message: String?
        + fileName: String
        + lineNumber: Int
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.message: Optional[str] = self._optional_str_value("message")
        self.file_name: str = self._str_value("fileName")
        self.line_number: int = self._int_value("lineNumber")

    def get_full_message(self) -> str:
        prefix = ""
        if self.file_name and self.line_number:
            prefix = f"{self.file_name}:{self.line_number} "
        return f"{prefix}{self.message}"


class ActionTestPerformanceMetricSummary(_AbstractRecord):
    """
    - ActionTestPerformanceMetricSummary
      * Kind: object
      * Properties:
        + displayName: String
        + unitOfMeasurement: String
        + measurements: [Double]
        + identifier: String?
        + baselineName: String?
        + baselineAverage: Double?
        + maxPercentRegression: Double?
        + maxPercentRelativeStandardDeviation: Double?
        + maxRegression: Double?
        + maxStandardDeviation: Double?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.display_name: str = self._str_value("displayName")
        self.unit_of_measurement: str = self._str_value("unitOfMeasurement")
        self.measurements: List[float] = self._array_float_values("measurements")
        self.identifier: Optional[str] = self._optional_str_value("identifier")
        self.baseline_name: Optional[str] = self._optional_str_value("baselineName")
        self.baseline_average: Optional[float] = self._optional_float_value("baselineAverage")
        self.max_percent_regression: Optional[float] = self._optional_float_value("maxPercentRegression")
        self.max_percent_relative_standard_deviation: Optional[float] = self._optional_float_value(
            "maxPercentRelativeStandardDeviation",
        )
        self.max_regression: Optional[float] = self._optional_float_value("maxRegression")
        self.max_standard_deviation: Optional[float] = self._optional_float_value("maxStandardDeviation")


class ActionTestPlanRunSummaries(_AbstractRecord):
    """
    - ActionTestPlanRunSummaries
      * Kind: object
      * Properties:
        + summaries: [ActionTestPlanRunSummary]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.summaries: List[ActionTestPlanRunSummary] = self._array_values("summaries", ActionTestPlanRunSummary)


class ActionTestPlanRunSummary(_ActionAbstractTestSummary):
    """
    - ActionTestPlanRunSummary
      * Supertype: ActionAbstractTestSummary
      * Kind: object
      * Properties:
        + testableSummaries: [ActionTestableSummary]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.testable_summaries: List[ActionTestableSummary] = self._array_values(
            "testableSummaries",
            ActionTestableSummary,
        )


class ActionTestSummary(_AbstractRecord):
    """
    - ActionTestSummary
      * Supertype: ActionTestSummaryIdentifiableObject
      * Kind: object
      * Properties:
        + testStatus: String
        + duration: Double
        + performanceMetrics: [ActionTestPerformanceMetricSummary
        + failureSummaries: [ActionTestFailureSummary]
        + skipNoticeSummary: ActionTestNoticeSummary?
        + activitySummaries: [ActionTestActivitySummary]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.test_status: str = self._str_value("testStatus")
        self.duration: float = self._float_value("duration")
        self.performance_metrics: List[ActionTestPerformanceMetricSummary] = self._array_values(
            "performanceMetrics",
            ActionTestPerformanceMetricSummary,
        )
        self.failure_summaries: List[ActionTestFailureSummary] = self._array_values(
            "failureSummaries",
            ActionTestFailureSummary,
        )
        self.skip_notice_summary: Optional[ActionTestNoticeSummary] = self._optional_object_value(
            "skipNoticeSummary",
            ActionTestNoticeSummary,
        )
        self.activity_summaries: List[ActionTestActivitySummary] = self._array_values(
            "activitySummaries",
            ActionTestActivitySummary,
        )


class ActionTestSummaryIdentifiableObject(_ActionAbstractTestSummary):
    """
    - ActionTestSummaryIdentifiableObject
      * Supertype: ActionAbstractTestSummary
      * Kind: object
      * Properties:
        + identifier: String?
    """

    def __init__(
        self,
        data: Dict,
        xcresult: pathlib.Path,
        parent: Optional[Union[ActionTestSummaryGroup, ActionTestableSummary]] = None,
    ):
        super().__init__(data, xcresult)
        self.parent = parent
        self.identifier: Optional[str] = self._optional_str_value("identifier")

    def get_full_name(self) -> str:
        if self.parent is None:
            parent_name: Optional[str] = ""
        elif isinstance(self.parent, ActionTestSummaryGroup):
            parent_name = self.parent.get_full_name()
        elif isinstance(self.parent, ActionTestableSummary):
            parent_name = self.parent.name
        else:
            raise ValueError("Unknown parent type", self.parent)

        return ".".join([p for p in [parent_name, self.name] if p])


class ActionTestMetadata(ActionTestSummaryIdentifiableObject):
    """
    - ActionTestMetadata
      * Supertype: ActionTestSummaryIdentifiableObject
      * Kind: object
      * Properties:
        + testStatus: String
        + duration: Double?
        + summaryRef: Reference?
        + performanceMetricsCount: Int
        + failureSummariesCount: Int
        + activitySummariesCount: Int
    """

    def __init__(
        self,
        data: Dict,
        xcresult: pathlib.Path,
        parent: Optional[Union[ActionTestSummaryGroup, ActionTestableSummary]] = None,
    ):
        super().__init__(data, xcresult, parent)
        self.test_status: str = self._str_value("testStatus")
        self.duration: Optional[float] = self._optional_float_value("duration")
        self.summary_ref: Optional[Reference] = self._optional_object_value("summaryRef", Reference)
        self.performance_metrics_count: int = self._int_value("performanceMetricsCount")
        self.failure_summaries_count: int = self._int_value("failureSummariesCount")
        self.activity_summaries_count: int = self._int_value("activitySummariesCount")

    @property
    def summary(self) -> Optional[ActionTestSummary]:
        return self._get_referenced_object(self.summary_ref, ActionTestSummary)

    def _is_failure_status(self):
        return self.test_status == "Failure"

    def _get_activity_summaries(self) -> List[ActionTestActivitySummary]:
        return self.summary.activity_summaries if self.summary else []

    def _get_failure_summaries(self) -> List[ActionTestFailureSummary]:
        return self.summary.failure_summaries if self.summary else []

    def _get_error_summaries(self) -> List[ActionTestFailureSummary]:
        return [fs for fs in self._get_failure_summaries() if fs.associated_error]

    def is_error(self) -> bool:
        if not self._is_failure_status():
            return False
        return len(self._get_error_summaries()) > 0

    def is_failure(self) -> bool:
        if not self._is_failure_status():
            return False
        return len(self._get_error_summaries()) == 0

    def is_disabled(self) -> bool:
        # Disabled tests are completely excluded from reports
        return False

    def is_skipped(self) -> bool:
        return self.test_status == "Skipped"

    def get_error_message(self) -> str:
        if not self.is_error():
            raise ValueError("Test did not fail with error", self)
        return "\n".join([s.message for s in self._get_error_summaries() if s.message])

    def get_failure_message(self) -> str:
        if not self.is_failure():
            raise ValueError("Test did not fail with failure", self)
        return "\n".join([s.message for s in self._get_failure_summaries() if s.message])

    def get_skipped_message(self) -> str:
        if not self.is_skipped():
            raise ValueError("Test was not skipped", self)
        skip_summary = self.summary.skip_notice_summary if self.summary else None
        if skip_summary and skip_summary.message:
            return skip_summary.get_full_message()
        for activity_summary in self._get_activity_summaries():
            if activity_summary.title:
                return activity_summary.title
        return ""

    def get_error_type(self) -> str:
        if not self.is_error():
            raise ValueError("Test did not fail with error", self)
        for error_summary in self._get_error_summaries():
            # Make mypy happy
            if error_summary.associated_error and error_summary.associated_error.domain:
                return error_summary.associated_error.domain
        return ""

    def get_failure_type(self) -> str:
        if not self.is_failure():
            raise ValueError("Test did not fail with failure", self)
        for failure_summary in self._get_failure_summaries():
            if failure_summary.issue_type:
                return failure_summary.issue_type
        return ""

    def get_failure_description(self) -> Optional[str]:
        if not self._is_failure_status():
            raise ValueError("Test did not fail", self)
        message = []
        for failure_summary in self._get_failure_summaries():
            description = failure_summary.get_description()
            if description:
                message.append(description)

        for activity_summary in self._get_activity_summaries():
            description = activity_summary.get_description()
            if description:
                message.append(description)

        return "\n".join(message)

    def get_classname(self) -> str:
        classname = ""
        if not self.parent:
            if self.identifier:
                classname = self.identifier.rsplit("/", 1)[0]
        else:
            if self.parent.name:
                classname = self.parent.name
            elif isinstance(self.parent, ActionTestSummaryGroup) and self.parent.identifier:
                classname = self.parent.identifier.split("/")[-1]
        return classname

    def get_method_name(self) -> str:
        if self.name:
            return self.name
        elif self.identifier:
            return self.identifier.split("/")[-1]
        else:
            return ""


class ActionTestSummaryGroup(ActionTestSummaryIdentifiableObject):
    """
    - ActionTestSummaryGroup
      * Supertype: ActionTestSummaryIdentifiableObject
      * Kind: object
      * Properties:
        + duration: Double
        + subtests: [ActionTestSummaryIdentifiableObject]
    """

    def __init__(
        self,
        data: Dict,
        xcresult: pathlib.Path,
        parent: Optional[Union[ActionTestSummaryGroup, ActionTestableSummary]] = None,
    ):
        super().__init__(data, xcresult, parent)
        self.duration: float = self._float_value("duration")
        self.subtests: List[Union[ActionTestSummaryGroup, ActionTestMetadata]] = self._array_values(
            "subtests",
            ActionTestSummaryGroup,
            ActionTestMetadata,
        )
        for subtest in self.subtests:
            subtest.parent = self

    def get_subtests(self) -> List[ActionTestMetadata]:
        tests: List[ActionTestMetadata] = []
        for subtest in self.subtests:
            if isinstance(subtest, ActionTestMetadata):
                tests.append(subtest)
            elif isinstance(subtest, ActionTestSummaryGroup):
                tests.extend(subtest.get_subtests())
            else:
                raise ValueError("Unknown subtests type", subtest)
        return tests


class ActionTestableSummary(_ActionAbstractTestSummary):
    """
    - ActionTestableSummary
      * Supertype: ActionAbstractTestSummary
      * Kind: object
      * Properties:
        + projectRelativePath: String?
        + targetName: String?
        + testKind: String?
        + tests: [ActionTestSummaryIdentifiableObject]
        + diagnosticsDirectoryName: String?
        + failureSummaries: [ActionTestFailureSummary]
        + testLanguage: String?
        + testRegion: String?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.project_relative_path: Optional[str] = self._optional_str_value("projectRelativePath")
        self.target_name: Optional[str] = self._optional_str_value("targetName")
        self.test_kind: Optional[str] = self._optional_str_value("testKind")
        self.tests: List[Union[ActionTestSummaryGroup, ActionTestMetadata]] = self._array_values(
            "tests",
            ActionTestSummaryGroup,
            ActionTestMetadata,
        )
        self.diagnostics_directory_name: Optional[str] = self._optional_str_value("diagnosticsDirectoryName")
        self.failure_summaries: List[ActionTestFailureSummary] = self._array_values(
            "failureSummaries",
            ActionTestFailureSummary,
        )
        self.test_language: Optional[str] = self._optional_str_value("testLanguage")
        self.test_region: Optional[str] = self._optional_str_value("testRegion")
        for test in self.tests:
            test.parent = self

    def get_tests(self) -> List[ActionTestMetadata]:
        tests: List[ActionTestMetadata] = []
        for test in self.tests:
            if isinstance(test, ActionTestMetadata):
                tests.append(test)
            elif isinstance(test, ActionTestSummaryGroup):
                tests.extend(test.get_subtests())
            else:
                raise ValueError("Unknown test type", test)
        return tests


class ActionsInvocationMetadata(_AbstractRecord):
    """
    - ActionsInvocationMetadata
      * Kind: object
      * Properties:
        + creatingWorkspaceFilePath: String
        + uniqueIdentifier: String
        + schemeIdentifier: EntityIdentifier?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.creating_workspace_file_path: str = self._str_value("creatingWorkspaceFilePath")
        self.unique_identifier: str = self._str_value("uniqueIdentifier")
        self.scheme_identifier: Optional[EntityIdentifier] = self._optional_object_value(
            "schemeIdentifier",
            EntityIdentifier,
        )


class ActionsInvocationRecord(_AbstractRecord):
    """
    - ActionsInvocationRecord
      * Kind: object
      * Properties:
        + metadataRef: Reference?
        + metrics: ResultMetrics
        + issues: ResultIssueSummaries
        + actions: [ActionRecord]
        + archive: ArchiveInfo?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.metadata_ref: Optional[Reference] = self._optional_object_value("metadataRef", Reference)
        self.metrics: ResultMetrics = self._object_value("metrics", ResultMetrics)
        self.issues: ResultIssueSummaries = self._object_value("issues", ResultIssueSummaries)
        self.actions: List[ActionRecord] = self._array_values("actions", ActionRecord)
        self.archive: Optional[ArchiveInfo] = self._optional_object_value("archive", ArchiveInfo)

    @classmethod
    def from_xcresult(cls, xcresult: pathlib.Path):
        raw_actions_invocation_record = _get_cached_object_from_bundle(xcresult)
        return ActionsInvocationRecord(raw_actions_invocation_record, xcresult)

    @property
    def metadata(self) -> Optional[ActionsInvocationMetadata]:
        return self._get_referenced_object(self.metadata_ref, ActionsInvocationMetadata)


class ArchiveInfo(_AbstractRecord):
    """
    - ArchiveInfo
      * Kind: object
      * Properties:
        + path: String?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.path: Optional[str] = self._optional_str_value("path")


class CodeCoverageInfo(_AbstractRecord):
    """
    - CodeCoverageInfo
      * Kind: object
      * Properties:
        + hasCoverageData: Bool
        + reportRef: Reference?
        + archiveRef: Reference?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.has_coverage_data: bool = self._bool_value("hasCoverageData")
        self.report_ref: Optional[Reference] = self._optional_object_value("reportRef", Reference)
        self.archive_ref: Optional[Reference] = self._optional_object_value("archiveRef", Reference)


class DocumentLocation(_AbstractRecord):
    """
    - DocumentLocation
      * Kind: object
      * Properties:
        + url: String
        + concreteTypeName: String
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.url: str = self._str_value("url")
        self.concrete_type_name: str = self._str_value("concreteTypeName")


class EntityIdentifier(_AbstractRecord):
    """
    - EntityIdentifier
        * Kind: object
        * Properties:
          + entityName: String
          + containerName: String
          + entityType: String
          + sharedState: String
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.entity_name: str = self._str_value("entityName")
        self.container_name: str = self._str_value("containerName")
        self.entity_type: str = self._str_value("entityType")
        self.shared_state: str = self._str_value("sharedState")


class IssueSummary(_AbstractRecord):
    """
    - IssueSummary
      * Kind: object
      * Properties:
        + issueType: String
        + message: String
        + producingTarget: String?
        + documentLocationInCreatingWorkspace: DocumentLocation?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.issue_type: str = self._str_value("issueType")
        self.message: str = self._str_value("message")
        self.producing_target: Optional[str] = self._optional_str_value("producingTarget")
        self.document_location_in_creating_workspace: Optional[DocumentLocation] = self._optional_object_value(
            "documentLocationInCreatingWorkspace",
            DocumentLocation,
        )


class Reference(_AbstractRecord):
    """
    - Reference
      * Kind: object
      * Properties:
        + id: String
        + targetType: TypeDefinition?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.id: str = self._str_value("id")
        self.target_type: Optional[TypeDefinition] = self._optional_object_value("targetType", TypeDefinition)


class ResultIssueSummaries(_AbstractRecord):
    """
    - ResultIssueSummaries
      * Kind: object
      * Properties:
        + analyzerWarningSummaries: [IssueSummary]
        + errorSummaries: [IssueSummary]
        + testFailureSummaries: [TestFailureIssueSummary]
        + warningSummaries: [IssueSummary]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.analyzer_warning_summaries: List[IssueSummary] = self._array_values(
            "analyzerWarningSummaries",
            IssueSummary,
        )
        self.error_summaries: List[IssueSummary] = self._array_values("errorSummaries", IssueSummary)
        self.test_failure_summaries: List[TestFailureIssueSummary] = self._array_values(
            "testFailureSummaries",
            TestFailureIssueSummary,
        )
        self.warning_summaries: List[IssueSummary] = self._array_values("warningSummaries", IssueSummary)


class ResultMetrics(_AbstractRecord):
    """
    - ResultMetrics
      * Kind: object
      * Properties:
        + analyzerWarningCount: Int
        + errorCount: Int
        + testsCount: Int
        + testsFailedCount: Int
        + testsSkippedCount: Int
        + warningCount: Int
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.analyzer_warning_count: int = self._int_value("analyzerWarningCount")
        self.error_count: int = self._int_value("errorCount")
        self.tests_count: int = self._int_value("testsCount")
        self.tests_failed_count: int = self._int_value("testsFailedCount")
        self.tests_skipped_count: int = self._int_value("testsSkippedCount")
        self.warning_count: int = self._int_value("warningCount")


class SortedKeyValueArray(_AbstractRecord):
    """
    - SortedKeyValueArray
      * Kind: object
      * Properties:
        + storage: [SortedKeyValueArrayPair]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.storage: List[SortedKeyValueArrayPair] = self._array_values("storage", SortedKeyValueArrayPair)


class SortedKeyValueArrayPair(_AbstractRecord):
    """
    - SortedKeyValueArrayPair
      * Kind: object
      * Properties:
        + key: String
        + value: SchemaSerializable
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.key: str = self._str_value("key")
        self.value: SchemaSerializable = self._schema_serializable_value("value")


class SourceCodeContext(_AbstractRecord):
    """
    - SourceCodeContext
      * Kind: object
      * Properties:
        + location: SourceCodeLocation?
        + callStack: [SourceCodeFrame]
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.location: Optional[SourceCodeLocation] = self._optional_object_value("location", SourceCodeLocation)
        self.callStack: List[SourceCodeFrame] = self._array_values("callStack", SourceCodeFrame)


class SourceCodeFrame(_AbstractRecord):
    """
    - SourceCodeFrame
      * Kind: object
      * Properties:
        + addressString: String?
        + symbolInfo: SourceCodeSymbolInfo?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.addressString: Optional[str] = self._optional_str_value("addressString")
        self.symbolInfo: Optional[SourceCodeSymbolInfo] = self._optional_object_value(
            "symbolInfo",
            SourceCodeSymbolInfo,
        )


class SourceCodeLocation(_AbstractRecord):
    """
    - SourceCodeLocation
      * Kind: object
      * Properties:
        + filePath: String?
        + lineNumber: Int?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.file_path: Optional[str] = self._str_value("filePath")
        self.line_number: Optional[int] = self._int_value("lineNumber")


class SourceCodeSymbolInfo(_AbstractRecord):
    """
    - SourceCodeSymbolInfo
      * Kind: object
      * Properties:
        + imageName: String?
        + symbolName: String?
        + location: SourceCodeLocation?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.imageName: Optional[str] = self._optional_str_value("imageName")
        self.symbolName: Optional[str] = self._optional_str_value("symbolName")
        self.location: Optional[SourceCodeLocation] = self._optional_object_value("location", SourceCodeLocation)


class TestAssociatedError(_AbstractRecord):
    """
    - TestAssociatedError
      * Kind: object
      * Properties:
        + domain: String?
        + code: Int?
        + userInfo: SortedKeyValueArray?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.domain: Optional[str] = self._optional_str_value("domain")
        self.code: Optional[int] = self._optional_int_value("code")
        self.user_info: Optional[SortedKeyValueArray] = self._optional_object_value("userInfo", SortedKeyValueArray)


class TestFailureIssueSummary(IssueSummary):
    """
    - TestFailureIssueSummary
      * Supertype: IssueSummary
      * Kind: object
      * Properties:
        + testCaseName: String
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.test_case_name: str = self._str_value("testCaseName")


class TypeDefinition(_AbstractRecord):
    """
    - TypeDefinition
      * Kind: object
      * Properties:
        + name: String
        + supertype: TypeDefinition?
    """

    def __init__(self, data: Dict, xcresult: pathlib.Path):
        super().__init__(data, xcresult)
        self.name: str = self._str_value("name")
        self.supertype: Optional[TypeDefinition] = self._optional_object_value("supertype", TypeDefinition)
