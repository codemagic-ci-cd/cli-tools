from __future__ import annotations

import json
import pathlib
from typing import List

import pytest

from codemagic.google.resources.google_play import Track


@pytest.fixture
def mock_tracks() -> List[Track]:
    mock_response_path = pathlib.Path(__file__).parent / "mocks" / "google_play_tracks.json"
    tracks_response = json.loads(mock_response_path.read_text())
    return [Track(**track) for track in tracks_response]
