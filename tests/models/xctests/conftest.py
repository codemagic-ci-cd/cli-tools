import json
import pathlib

import pytest
from codemagic.models.xctests.xcresult import ActionsInvocationRecord


@pytest.fixture(scope="session")
def mocks_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "mocks"


@pytest.fixture
def action_invocations_record(mocks_dir) -> ActionsInvocationRecord:
    with (mocks_dir / "actions_invocation_record.json").open() as fd:
        data = json.load(fd)
    return ActionsInvocationRecord(data, pathlib.Path("Test.xcresult"))
