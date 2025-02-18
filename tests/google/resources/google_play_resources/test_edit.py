from __future__ import annotations

from codemagic.google.resources.google_play_resources import Edit


def test_edit_initialization(api_google_play_edit: dict):
    edit = Edit(**api_google_play_edit)
    assert edit.dict() == api_google_play_edit
