import os
import unittest

import pytest

from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient
from codemagic.google_play.resources import TrackName


# @pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Google Play Developer API access')
@pytest.mark.usefixtures('class_google_play_api_client')
class ApiTests(unittest.TestCase):
    api_client: GooglePlayDeveloperAPIClient

    def _service_exists(self):
        return self.api_client._service_instance is not None

    def test_get_edit_and_track_information(self):
        assert not self._service_exists()
        edit = self.api_client.create_edit()
        assert self._service_exists()
        assert edit.id is not None
        assert edit.expiryTimeSeconds is not None

        track = self.api_client.get_track_information(edit.id, TrackName.INTERNAL)
        assert track.releases
        for release in track.releases:
            assert release.versionCodes

        self.api_client.delete_edit(edit.id)
        assert not self._service_exists()
