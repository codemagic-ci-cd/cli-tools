import json
import pathlib

import pytest


@pytest.fixture
def api_google_play_edit() -> dict:
    mock_path = pathlib.Path(__file__).parent / "mocks" / "google_play_edit.json"
    return json.loads(mock_path.read_text())


@pytest.fixture
def api_google_play_track() -> dict:
    mock_path = pathlib.Path(__file__).parent / "mocks" / "google_play_track.json"
    return json.loads(mock_path.read_text())


@pytest.fixture
def api_firebase_release() -> dict:
    mock_path = pathlib.Path(__file__).parent / "mocks" / "firebase_release.json"
    return json.loads(mock_path.read_text())
