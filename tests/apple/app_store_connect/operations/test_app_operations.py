import pytest

from codemagic_cli_tools.apple.resources import App
from codemagic_cli_tools.apple.resources import ResourceType
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
class AppOperationsTest(OperationsTestsBase):

    def test_list_apps(self):
        apps = self.api_client.apps.list()
        assert len(apps) > 0
        for app in apps:
            assert isinstance(app, App)
            assert app.type is ResourceType.APP
