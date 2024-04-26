import os

import pytest
from codemagic.apple.resources import App
from codemagic.apple.resources import ResourceId
from codemagic.tools import AppStoreConnect


@pytest.mark.skipif(
    not os.environ.get("RUN_LIVE_API_TESTS"),
    reason="Live App Store Connect API access",
)
def test_get_app(app_store_connect: AppStoreConnect):
    app = app_store_connect.get_app(ResourceId("1481211155"))
    assert isinstance(app, App)
    assert app.id == "1481211155"
