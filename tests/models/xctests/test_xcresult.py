import json
import pathlib

import pytest

from codemagic.models.xctests.xcresult import ActionsInvocationRecord
from codemagic.models.xctests.xcresult import ActionTestPlanRunSummary


@pytest.mark.skip(reason='Test is not ready')
def test_actions_invocation_record():
    test_result = json.load(open('/tmp/test-result.json'))
    xcresult = pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-merged.xcresult').expanduser()
    air = ActionsInvocationRecord(test_result, xcresult)
    tests_refs = [action.action_result.tests_ref for action in air.actions]
    assert len([ref.id for ref in tests_refs if tests_refs]) == 2


@pytest.mark.skip(reason='Test is not ready')
def test_action_test_plan_run_summary():
    test_run_summary = json.load(open('/tmp/test-reference-1.json'))
    xcresult = pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-merged.xcresult').expanduser()
    trs = ActionTestPlanRunSummary(test_run_summary, xcresult)
    print(trs)
