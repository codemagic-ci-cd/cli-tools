import json
import pathlib

import pytest

from codemagic.models.xctests.xcresult import ActionsInvocationRecord


@pytest.fixture(scope='session')
def action_invocations_record() -> ActionsInvocationRecord:
    mock_json_path = pathlib.Path(__file__).parent / 'mocks' / 'actions_invocation_record.json'
    with mock_json_path.open() as fd:
        data = json.load(fd)
    return ActionsInvocationRecord(data, pathlib.Path('Test.xcresult'))
