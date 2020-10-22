import json

import pytest

from codemagic.models.xctests.xcresult import ActionsInvocationRecord
from codemagic.models.xctests.xcresult import ActionTestPlanRunSummary


@pytest.mark.skip(reason='Test is not ready')
def test_actions_invocation_record():
    test_result = json.load(open('/tmp/test-result.json'))
    air = ActionsInvocationRecord(test_result)
    assert len(air.tests_refs) == 2
    print(air)
    for r in air.tests_refs:
        print(r.id)


@pytest.mark.skip(reason='Test is not ready')
def test_Action_Test_Plan_Run_Summary():
    test_run_summary = json.load(open('/tmp/test-reference-1.json'))
    trs = ActionTestPlanRunSummary(test_run_summary)
    print(trs)
