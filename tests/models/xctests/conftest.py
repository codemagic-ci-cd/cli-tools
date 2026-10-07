import json
import pathlib
from typing import Dict

import pytest


@pytest.fixture(scope="session")
def mocks_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "mocks"


@pytest.fixture
def test_results_summary_dict(mocks_dir) -> Dict:
    mock_path = mocks_dir / "test_results_summary.json"
    return json.loads(mock_path.read_text())


@pytest.fixture
def test_results_tests_dict(mocks_dir) -> Dict:
    mock_path = mocks_dir / "test_results_tests.json"
    return json.loads(mock_path.read_text())
