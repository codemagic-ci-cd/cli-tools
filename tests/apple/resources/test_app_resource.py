from __future__ import annotations

from codemagic.apple.resources import App


def test_app_initialization(api_app):
    app = App(api_app)
    assert app.dict() == api_app
