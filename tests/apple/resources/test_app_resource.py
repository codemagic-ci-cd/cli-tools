from __future__ import annotations

from codemagic.apple.resources import App


def test_app_initialization(api_app):
    app = App(api_app)
    assert app.dict() == api_app


def test_app_with_empty_relationship(api_app):
    api_app["relationships"]["ciProduct"] = {}
    app = App(api_app)
    assert app.relationships.ciProduct is None
    assert "ciProduct" not in app.dict()["relationships"]
