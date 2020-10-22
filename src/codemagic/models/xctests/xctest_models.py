from __future__ import annotations

from abc import ABCMeta
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

T = TypeVar('T')


class ResultBase(metaclass=ABCMeta):
    def __init__(self, data: Dict):
        self._data = data
        self.type = data['_type']['_name']

    def _value(self, key: str, default: Optional[T] = None) -> T:
        return self._data.get(key, {}).get('_value', default)

    def _values(self, key: str, default: Optional[List[T]] = None) -> List[T]:
        return self._data.get(key, {}).get('_values', default or [])


class ActionTestPlanRunSummaries(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        summaries: List[Dict] = self._values('summaries')
        self.summaries: List[ActionTestPlanRunSummary] = [
            ActionTestPlanRunSummary(summary_data) for summary_data in summaries]


class ActionAbstractTestSummary(ResultBase, metaclass=ABCMeta):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.name: Optional[str] = self._value('name')


class ActionTestPlanRunSummary(ActionAbstractTestSummary):
    def __init__(self, data: Dict):
        super().__init__(data)
        testable_summaries: List[Dict] = self._values('testableSummaries')
        self.testable_summaries: List[ActionTestableSummary] = [
            ActionTestableSummary(summary_data) for summary_data in testable_summaries]


class ActionTestableSummary(ActionAbstractTestSummary):
    def __init__(self, data: Dict):
        super().__init__(data)
        self._project_relative_path: Optional[str] = self._value('projectRelativePath')
        self.target_name: Optional[str] = self._value('targetName')
        self.test_kind: Optional[str] = self._value('testKind')
        tests: List[Dict] = self._values('tests')
        self.tests: List[ActionTestSummaryIdentifiableObject] = [
            ActionTestSummaryIdentifiableObject.create(test_data, self) for test_data in tests]


class ActionTestSummaryIdentifiableObject(ActionAbstractTestSummary):
    def __init__(self, data: Dict, parent: Union[ActionTestableSummary, ActionTestSummaryGroup]):
        super().__init__(data)
        self.identifier: Optional[str] = self._value('identifier')
        self.parent = parent

    @classmethod
    def create(cls,
               data: Dict,
               parent: Union[ActionTestableSummary, ActionTestSummaryGroup]) -> ActionTestSummaryIdentifiableObject:
        object_type = data['_type']['_name']
        if object_type == 'ActionTestSummaryGroup':
            return ActionTestSummaryGroup(data, parent)
        elif object_type == 'ActionTestMetadata':
            return ActionTestMetadata(data, parent)
        else:
            raise ValueError(f'Unsupported type: {object_type}')


class ActionTestSummaryGroup(ActionTestSummaryIdentifiableObject):
    def __init__(self, data: Dict, parent: Union[ActionTestableSummary, ActionTestSummaryGroup]):
        super().__init__(data, parent)
        self.duration: float = self._value('duration')
        subtests: List[Dict] = self._values('subtests')
        self.subtests: List[ActionTestSummaryIdentifiableObject] = [
            ActionTestSummaryIdentifiableObject.create(subtests_data, self)
            for subtests_data in subtests
        ]


class ActionTestMetadata(ActionTestSummaryIdentifiableObject):
    def __init__(self, data: Dict, parent: Union[ActionTestableSummary, ActionTestSummaryGroup]):
        super().__init__(data, parent)
        self.test_status: str = self._value('testStatus')
        self.duration: Optional[float] = self._value('duration')
        self.performance_metrics_count: int = self._value('performanceMetricsCount', 0)
        self.failure_summaries_count: int = self._value('failureSummariesCount', 0)
        self.activity_summaries_count: int = self._value('activitySummariesCount', 0)


class ActionRecord(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.scheme_command_name: str = self._value('schemeCommandName')
        self.scheme_task_name: str = self._value('schemeTaskName')
        self.title: Optional[str] = self._value('title')
        self.build_result = ActionResult(data['buildResult'])
        self.action_result = ActionResult(data['actionResult'])


class ActionResult(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.result_name: str = self._value('resultName')
        self.status: str = self._value('status')
        self.issues = ResultIssueSummaries(data['issues']) if 'issues' in data else None
        self.timeline_ref = Reference(data['timelineRef']) if 'timelineRef' in data else None
        self.log_ref = Reference(data['logRef']) if 'logRef' in data else None
        self.tests_ref = Reference(data['testsRef']) if 'testsRef' in data else None
        self.diagnostics_ref = Reference(data['diagnosticsRef']) if 'diagnosticsRef' in data else None


class Reference(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.id: str = self._value('id')
        self.target_type = TypeDefinition(data['targetType']) if 'targetType' in data else None


class TypeDefinition(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.name: str = self._value('name')
        self.supertype = TypeDefinition(data['supertype']) if 'supertype' in data else None


class DocumentLocation(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.url: str = self._value('url')
        self.concrete_type_name: str = data["concreteTypeName"]["_value"]


class IssueSummary(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.issue_type: str = self._value('issueType')
        self.message: str = self._value('message')
        self.producing_target: Optional[str] = self._value('producingTarget')
        self.document_location_in_creating_workspace: Optional[DocumentLocation] = None
        if 'documentLocationInCreatingWorkspace' in data:
            self.document_location_in_creating_workspace = DocumentLocation(data['documentLocationInCreatingWorkspace'])


class ResultIssueSummaries(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        analyzer_warning_summaries: List[Dict] = self._values('analyzerWarningSummaries')
        error_summaries: List[Dict] = self._values('errorSummaries')
        test_failure_summaries: List[Dict] = self._values('testFailureSummaries')
        warning_summaries: List[Dict] = self._values('warningSummaries')
        self.analyzer_warning_summaries = [IssueSummary(summary_data) for summary_data in analyzer_warning_summaries]
        self.error_summaries = [IssueSummary(summary_data) for summary_data in error_summaries]
        self.test_failure_summaries = [TestFailureIssueSummary(summary_data) for summary_data in test_failure_summaries]
        self.warning_summaries = [IssueSummary(summary_data) for summary_data in warning_summaries]


class TestFailureIssueSummary(IssueSummary):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.test_case_name: str = self._value('testCaseName')


class ActionsInvocationRecord(ResultBase):
    def __init__(self, data: Dict):
        super().__init__(data)
        actions: List[Dict] = self._values('actions')
        self.actions = [ActionRecord(action_data) for action_data in actions]
        self.issues = ResultIssueSummaries(data['issues'])

    @property
    def tests_ref_ids(self):
        tests_refs = filter(None, (a.action_result.tests_ref for a in self.actions))
        return [tests_ref.id for tests_ref in tests_refs]
