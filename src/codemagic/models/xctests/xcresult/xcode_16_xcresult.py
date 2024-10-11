from __future__ import annotations

import dataclasses
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import cast

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    AttributeName: TypeAlias = str
    DictKey: TypeAlias = str


XcResultModelT = TypeVar("XcResultModelT", bound="XcResultModel")
LiteralValueT = TypeVar("LiteralValueT", bool, str, int, float)


@dataclasses.dataclass
class XcResultModel(ABC):
    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]]

    @classmethod
    def _resolve_literal_values(cls, d: Dict[DictKey, Any]) -> Dict[AttributeName, LiteralValueT]:
        return {
            attr_name: cast(LiteralValueT, d[dict_key])
            for attr_name, dict_key in cls.__literal_attribute_name_mapping__.items()
        }

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[XcResultModelT], d: Dict[DictKey, Any]) -> XcResultModelT:
        """
        Load model from `xcresulttool get test-results <subcommand>` output
        """
        literal_values = cls._resolve_literal_values(d)
        return cls(**literal_values)


@dataclasses.dataclass
class XcTestDetails(XcResultModel):
    devices: List[XcDevice]
    duration: str
    has_media_attachments: bool
    has_performance_metrics: bool
    start_time: float
    test_description: str
    test_identifier: str
    test_name: str
    test_plan_configurations: List[XcTestPlanConfiguration]
    test_result: str
    test_runs: List[XcTestRun]

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "duration": "duration",
        "has_media_attachments": "hasMediaAttachments",
        "has_performance_metrics": "hasPerformanceMetrics",
        "start_time": "startTime",
        "test_description": "testDescription",
        "test_identifier": "testIdentifier",
        "test_name": "testName",
        "test_result": "testResult",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestDetails:
        return cls(
            devices=[XcDevice.from_dict(device) for device in d["devices"]],
            test_plan_configurations=[
                XcTestPlanConfiguration.from_dict(config) for config in d["testPlanConfigurations"]
            ],
            test_runs=[XcTestRun.from_dict(run) for run in d["testRuns"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )


@dataclasses.dataclass
class XcTestResultsSummary(XcResultModel):
    """
    Model definitions for `xcresulttool get test-results summary` output
    """

    devices_and_configurations: List[XcDevicesAndConfigurations]
    environment_description: str
    expected_failures: int
    failed_tests: int
    finish_time: float
    passed_tests: int
    result: str
    skipped_tests: int
    start_time: float
    statistics: List[XcTestStatistic]
    test_failures: List[XcTestFailure]
    title: str
    top_insights: List[XcTestInsight]
    total_test_count: int

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "environment_description": "environmentDescription",
        "expected_failures": "expectedFailures",
        "failed_tests": "failedTests",
        "finish_time": "finishTime",
        "passed_tests": "passedTests",
        "result": "result",
        "skipped_tests": "skippedTests",
        "start_time": "startTime",
        "title": "title",
        "total_test_count": "totalTestCount",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestResultsSummary:
        return cls(
            devices_and_configurations=[
                XcDevicesAndConfigurations.from_dict(dc) for dc in d["devicesAndConfigurations"]
            ],
            statistics=[XcTestStatistic.from_dict(statistic) for statistic in d["statistics"]],
            test_failures=[XcTestFailure.from_dict(failure) for failure in d["testFailures"]],
            top_insights=[XcTestInsight.from_dict(insight) for insight in d["topInsights"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )


@dataclasses.dataclass
class XcDevicesAndConfigurations(XcResultModel):
    device: XcDevice
    expected_failures: int
    failed_tests: int
    passed_tests: int
    skipped_tests: int
    test_plan_configuration: XcTestPlanConfiguration

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "expected_failures": "expectedFailures",
        "failed_tests": "failedTests",
        "passed_tests": "passedTests",
        "skipped_tests": "skippedTests",
    }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcDevicesAndConfigurations:
        return cls(
            device=XcDevice.from_dict(d["device"]),
            test_plan_configuration=XcTestPlanConfiguration.from_dict(d["testPlanConfiguration"]),
            **cls._resolve_literal_values(d),
        )


@dataclasses.dataclass
class XcTestStatistic(XcResultModel):
    subtitle: str
    title: str

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "subtitle": "subtitle",
        "title": "title",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestStatistic:
        return super().from_dict(d)


@dataclasses.dataclass
class XcTestFailure(XcResultModel):
    failure_text: str
    target_name: str
    test_identifier: int
    test_name: str

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "failure_text": "failureText",
        "target_name": "targetName",
        "test_identifier": "testIdentifier",
        "test_name": "testName",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestFailure:
        return super().from_dict(d)


@dataclasses.dataclass
class XcTestInsight(XcResultModel):
    """
    Attributes unknown
    """

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {}

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestInsight:
        return super().from_dict(d)


@dataclasses.dataclass
class XcTestResultsTests(XcResultModel):
    """
    Model definitions for `xcresulttool get test-results tests` output
    """

    devices: List[XcDevice]
    test_plans: List[XcTestPlan]
    test_plan_configurations: List[XcTestPlanConfiguration]

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {}

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestResultsTests:
        test_results_tests = cls(
            devices=[XcDevice.from_dict(device) for device in d["devices"]],
            test_plans=[XcTestPlan.from_dict(plan) for plan in d["testNodes"]],
            test_plan_configurations=[XcTestPlanConfiguration.from_dict(conf) for conf in d["testPlanConfigurations"]],
        )
        for plan in test_results_tests.test_plans:
            plan.parent = test_results_tests
        return test_results_tests


@dataclasses.dataclass
class XcTestNode(XcResultModel, ABC):
    name: str
    node_type: str
    result: str

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "name": "name",
        "node_type": "nodeType",
        "result": "result",
    }

    def is_failed(self) -> bool:
        return self.result.casefold() == "Failed".casefold()

    def is_skipped(self) -> bool:
        return self.result.casefold() == "Skipped".casefold()

    def is_passed(self) -> bool:
        return self.result.casefold() == "Passed".casefold()


@dataclasses.dataclass
class XcTestPlan(XcTestNode):
    test_bundles: List[XcTestBundle]
    parent: XcTestResultsTests = dataclasses.field(init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestPlan:
        test_plan = cls(
            test_bundles=[XcTestBundle.from_dict(bundle) for bundle in d["children"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )
        for test_bundle in test_plan.test_bundles:
            test_bundle.parent = test_plan
        return test_plan


@dataclasses.dataclass
class XcTestBundle(XcTestNode):
    test_suites: List[XcTestSuite]
    parent: XcTestPlan = dataclasses.field(init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestBundle:
        test_bundle = cls(
            test_suites=[XcTestSuite.from_dict(suite) for suite in d["children"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )
        for test_suite in test_bundle.test_suites:
            test_suite.parent = test_bundle
        return test_bundle


@dataclasses.dataclass
class XcTestSuite(XcTestNode):
    test_cases: List[XcTestCase]
    parent: XcTestBundle = dataclasses.field(init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestSuite:
        test_suite = cls(
            test_cases=[XcTestCase.from_dict(case) for case in d["children"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )
        for test_case in test_suite.test_cases:
            test_case.parent = test_suite
        return test_suite


@dataclasses.dataclass
class XcTestRunAction(XcTestNode):
    duration: str
    node_identifier: str

    __literal_attribute_name_mapping__ = {
        **XcTestNode.__literal_attribute_name_mapping__,
        "duration": "duration",
        "node_identifier": "nodeIdentifier",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestRunAction:
        return super().from_dict(d)


@dataclasses.dataclass
class XcTestCaseDetail(XcTestNode):
    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestCaseDetail:
        return super().from_dict(d)

    def _is_failure_message_node(self) -> bool:
        return self.node_type.casefold() == "Failure Message".casefold()

    def is_failure_message(self) -> bool:
        return self._is_failure_message_node() and self.is_failed()

    def is_skipped_message(self) -> bool:
        return self._is_failure_message_node() and self.is_skipped()


@dataclasses.dataclass
class XcTestCase(XcTestRunAction):
    details: List[XcTestCaseDetail] = dataclasses.field(default_factory=list)
    parent: XcTestSuite = dataclasses.field(init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestCase:
        return cls(
            details=[XcTestCaseDetail.from_dict(detail) for detail in d.get("children", [])],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )

    def get_failure_messages(self) -> List[str]:
        return [detail.name for detail in self.details if detail.is_failure_message() and detail.name]

    def get_skipped_messages(self) -> List[str]:
        return [detail.name for detail in self.details if detail.is_skipped_message() and detail.name]

    @classmethod
    def is_disabled(cls) -> bool:
        # Disabled tests are completely excluded from reports
        return False

    @classmethod
    def is_error(cls) -> bool:
        # Errors are classified as failures
        return False

    def get_duration(self) -> float:
        if not self.duration:
            return 0.0
        duration = self.duration.replace(",", ".")
        if duration.endswith("s"):
            duration = duration[:-1]
        return float(duration)

    def get_classname(self) -> str:
        if self.node_identifier:
            return self.node_identifier.split("/", maxsplit=1)[0]
        test_suite = self.parent
        if test_suite.name:
            return test_suite.name
        return ""

    def get_method_name(self) -> str:
        if self.name:
            return self.name
        elif self.node_identifier:
            return self.node_identifier.split("/")[-1]
        return ""


@dataclasses.dataclass
class XcTestRun(XcTestNode):
    test_run_actions: List[XcTestRunAction]
    details: str
    duration: str
    node_identifier: str

    __literal_attribute_name_mapping__ = {
        **XcTestNode.__literal_attribute_name_mapping__,
        "details": "details",
        "duration": "duration",
        "node_identifier": "nodeIdentifier",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestRun:
        return cls(
            test_run_actions=[XcTestRunAction.from_dict(action) for action in d["children"]],
            **cls._resolve_literal_values(d),  # type: ignore[arg-type]
        )


@dataclasses.dataclass
class XcDevice(XcResultModel):
    architecture: str
    device_id: str
    device_name: str
    model_name: str
    os_version: str
    platform: str

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "architecture": "architecture",
        "device_id": "deviceId",
        "device_name": "deviceName",
        "model_name": "modelName",
        "os_version": "osVersion",
        "platform": "platform",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcDevice:
        return super().from_dict(d)


@dataclasses.dataclass
class XcTestPlanConfiguration(XcResultModel):
    configuration_id: str
    configuration_name: str

    __literal_attribute_name_mapping__: ClassVar[Dict[AttributeName, DictKey]] = {
        "configuration_id": "configurationId",
        "configuration_name": "configurationName",
    }

    @classmethod
    def from_dict(cls, d: Dict[DictKey, Any]) -> XcTestPlanConfiguration:
        return super().from_dict(d)
