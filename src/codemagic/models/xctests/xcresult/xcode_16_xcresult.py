from __future__ import annotations

import dataclasses
import enum
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

XcSchemaModelT = TypeVar("XcSchemaModelT", bound="XcSchemaModel")


class XcTestResult(enum.StrEnum):
    PASSED = "Passed"
    FAILED = "Failed"
    SKIPPED = "Skipped"
    EXPECTED_FAILURE = "Expected Failure"
    UNKNOWN = "unknown"


class XcTestNodeType(enum.StrEnum):
    TEST_PLAN = "Test Plan"
    UNIT_TEST_BUNDLE = "Unit test bundle"
    UI_TEST_BUNDLE = "UI test bundle"
    TEST_SUITE = "Test Suite"
    TEST_CASE = "Test Case"
    DEVICE = "Device"
    TEST_PLAN_CONFIGURATION = "Test Plan Configuration"
    ARGUMENTS = "Arguments"
    REPETITION = "Repetition"
    TEST_CASE_RUN = "Test Case Run"
    FAILURE_MESSAGE = "Failure Message"
    SOURCE_CODE_REFERENCE = "Source Code Reference"
    ATTACHMENT = "Attachment"
    EXPRESSION = "Expression"
    TEST_VALUE = "Test Value"


@dataclasses.dataclass
class XcSchemaModel(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls: Type[XcSchemaModelT], d: Dict[str, Any]) -> XcSchemaModelT:
        """
        Load model from `xcresulttool get test-results <subcommand>` output
        """
        raise NotImplementedError()


@dataclasses.dataclass
class XcSummary(XcSchemaModel):
    """
    Model definitions for `xcresulttool get test-results summary` output.
    Check schema with `xcrun xcresulttool help get test-results summary`.
    """

    title: str
    environment_description: str
    top_insights: List[XcTestInsight]
    result: XcTestResult
    total_test_count: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    expected_failures: int
    statistics: List[XcTestStatistic]
    devices_and_configurations: List[XcTestPlanConfiguration]
    test_failures: List[XcTestFailure]
    start_time: Optional[float] = None
    finish_time: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcSummary:
        return cls(
            title=d["title"],
            environment_description=d["environmentDescription"],
            top_insights=[XcTestInsight.from_dict(insight) for insight in d["topInsights"]],
            result=XcTestResult(d["result"]),
            total_test_count=d["totalTestCount"],
            passed_tests=d["passedTests"],
            failed_tests=d["failedTests"],
            skipped_tests=d["skippedTests"],
            expected_failures=d["expectedFailures"],
            statistics=[XcTestStatistic.from_dict(statistic) for statistic in d["statistics"]],
            devices_and_configurations=[XcTestPlanConfiguration.from_dict(dc) for dc in d["devicesAndConfigurations"]],
            test_failures=[XcTestFailure.from_dict(failure) for failure in d["testFailures"]],
            start_time=d.get("startTime"),
            finish_time=d.get("finishTime"),
        )


@dataclasses.dataclass
class XcTestPlanConfiguration(XcSchemaModel):
    device: XcDevice
    test_plan_configuration: XcConfiguration
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    expected_failures: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTestPlanConfiguration:
        return cls(
            device=XcDevice.from_dict(d["device"]),
            test_plan_configuration=XcConfiguration.from_dict(d["testPlanConfiguration"]),
            passed_tests=d["passedTests"],
            failed_tests=d["failedTests"],
            skipped_tests=d["skippedTests"],
            expected_failures=d["expectedFailures"],
        )


@dataclasses.dataclass
class XcTestStatistic(XcSchemaModel):
    subtitle: str
    title: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTestStatistic:
        return cls(
            title=d["title"],
            subtitle=d["subtitle"],
        )


@dataclasses.dataclass
class XcTestFailure(XcSchemaModel):
    test_name: str
    target_name: str
    failure_text: str
    test_identifier: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTestFailure:
        return cls(
            test_name=d["testName"],
            target_name=d["targetName"],
            failure_text=d["failureText"],
            test_identifier=d["testIdentifier"],
        )


@dataclasses.dataclass
class XcTestInsight(XcSchemaModel):
    impact: str
    category: str
    text: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTestInsight:
        return cls(
            impact=d["impact"],
            category=d["category"],
            text=d["text"],
        )


@dataclasses.dataclass
class XcTests(XcSchemaModel):
    """
    Model definitions for `xcresulttool get test-results tests` output.
    Check schema with `xcrun xcresulttool help get test-results tests.
    """

    devices: List[XcDevice]
    test_nodes: List[XcTestNode]
    test_plan_configurations: List[XcConfiguration]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTests:
        tests = cls(
            devices=[XcDevice.from_dict(device) for device in d["devices"]],
            test_nodes=[XcTestNode.from_dict(node) for node in d["testNodes"]],
            test_plan_configurations=[XcConfiguration.from_dict(conf) for conf in d["testPlanConfigurations"]],
        )
        for node in tests.test_nodes:
            node.parent = tests
        return tests


@dataclasses.dataclass
class XcTestNode(XcSchemaModel):
    # Required properties
    node_type: XcTestNodeType
    name: str
    # Optional properties with defaults
    tags: List[str] = dataclasses.field(default_factory=list)
    children: List[XcTestNode] = dataclasses.field(default_factory=list)
    # Optional properties
    node_identifier: Optional[str] = None
    details: Optional[str] = None
    duration: Optional[str] = None
    result: Optional[XcTestResult] = None

    parent: Union[XcTests, XcTestNode] = dataclasses.field(init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcTestNode:
        result_value = d.get("result")
        node = cls(
            node_type=XcTestNodeType(d["nodeType"]),
            name=d["name"],
            tags=d.get("tags", []),
            children=[XcTestNode.from_dict(child) for child in d.get("children", [])],
            node_identifier=d.get("nodeIdentifier"),
            details=d.get("details"),
            duration=d.get("duration"),
            result=XcTestResult(result_value) if result_value else None,
        )
        for child in node.children:
            child.parent = node
        return node

    def iter_children(self, child_type: XcTestNodeType) -> Iterator[XcTestNode]:
        if self.node_type is child_type:
            yield self
        else:
            for child in self.children:
                yield from child.iter_children(child_type)

    def get_parent(self, parent_type: XcTestNodeType) -> Optional[XcTestNode]:
        if not isinstance(self.parent, XcTestNode):
            return None
        if self.parent.node_type is parent_type:
            return self.parent
        return self.parent.get_parent(parent_type)

    @classmethod
    def is_disabled(cls) -> bool:
        return False  # Disabled tests are completely excluded from reports

    def is_failed(self) -> bool:
        return self.result is XcTestResult.FAILED

    def is_skipped(self) -> bool:
        return self.result is XcTestResult.SKIPPED

    def is_passed(self) -> bool:
        return self.result is XcTestResult.PASSED

    def get_duration(self) -> float:
        if not self.duration:
            return 0.0
        duration = self.duration.replace(",", ".")
        if duration.endswith("s"):
            duration = duration[:-1]
        return float(duration)


@dataclasses.dataclass
class XcDevice(XcSchemaModel):
    device_name: str
    architecture: str
    model_name: str
    os_version: str
    device_id: Optional[str] = None
    platform: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcDevice:
        return cls(
            device_name=d["deviceName"],
            architecture=d["architecture"],
            model_name=d["modelName"],
            os_version=d["osVersion"],
            device_id=d.get("deviceId"),
            platform=d.get("platform"),
        )


@dataclasses.dataclass
class XcConfiguration(XcSchemaModel):
    configuration_id: str
    configuration_name: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> XcConfiguration:
        return cls(
            configuration_id=d["configurationId"],
            configuration_name=d["configurationName"],
        )
