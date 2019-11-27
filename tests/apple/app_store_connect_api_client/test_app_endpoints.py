import unittest

import pytest

from apple.resources import App
from apple.resources import ResourceType


@pytest.mark.skip(reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_api_client', 'class_logger')
class AppEndpointsTest(unittest.TestCase):

    def test_list_apps(self):
        apps = self.api_client.list_apps()
        assert len(apps) > 0
        for app in apps:
            assert isinstance(app, App)
            assert app.type is ResourceType.APP
