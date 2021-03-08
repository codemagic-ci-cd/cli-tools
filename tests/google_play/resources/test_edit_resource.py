from __future__ import annotations

from codemagic.google_play.resources import Edit


def test_edit_initialization(api_edit):
    edit = Edit(**api_edit)
    assert edit.dict() == api_edit
