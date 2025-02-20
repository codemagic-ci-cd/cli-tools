from __future__ import annotations

from codemagic.google.resources.google_play import AppEdit


def test_app_edit_initialization(api_google_play_app_edit: dict):
    edit = AppEdit(**api_google_play_app_edit)
    assert edit.dict() == api_google_play_app_edit
