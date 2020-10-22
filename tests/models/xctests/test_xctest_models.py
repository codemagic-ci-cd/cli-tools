import json

import pytest

from codemagic.models.xctests.xctest_models import ActionsInvocationRecord


@pytest.mark.skip(reason='Test is not ready')
def test_models():
    test_result = json.load(open('/tmp/test-result.json'))
    air = ActionsInvocationRecord(test_result)
    assert len(air.tests_ref_ids) == 2
