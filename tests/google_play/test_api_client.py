import os

import pytest

from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Google Play Developer API access')
def test_list_tracks(google_play_api_client: GooglePlayDeveloperAPIClient):
    tracks = google_play_api_client.list_tracks(package_name='io.codemagic.artemii.capybara')
    found_track_names = {t.track for t in tracks}
    assert found_track_names == {'production', 'beta', 'alpha', 'internal'}


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Google Play Developer API access')
def test_get_track(google_play_api_client: GooglePlayDeveloperAPIClient):
    track = google_play_api_client.get_track(
        package_name='io.codemagic.artemii.capybara',
        track_name='alpha',
    )
    assert track.dict() == {
        'releases': [
            {
                'name': '65 (0.0.42)',
                'status': 'completed',
                'versionCodes': ['65'],
            },
        ],
        'track': 'alpha',
    }
