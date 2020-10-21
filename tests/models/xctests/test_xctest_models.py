import json

from codemagic.models.xctests.xctest_models import ActionsInvocationRecord


def test_models():
    test_result = json.load(open('/tmp/test-result.json'))
    air = ActionsInvocationRecord(test_result)
    assert len(air.tests_ref_ids) == 2
