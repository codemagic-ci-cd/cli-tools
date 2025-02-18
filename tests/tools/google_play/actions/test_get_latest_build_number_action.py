from __future__ import annotations

import pytest

from codemagic.tools.google_play.arguments import GooglePlayArgument

credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS


@pytest.mark.parametrize(
    "tracks, expected_version_code",
    [
        ("alpha", 65),
        ("beta", 66),
        ("internal", 67),
        ((), 67),
        (("alpha", "production"), 65),
        (("beta", "production"), 66),
        (("internal", "production"), 67),
        (("alpha", "beta", "internal"), 67),
        (("alpha", "beta", "internal", "production"), 67),
    ],
)
def test_get_latest_build_number(tracks, expected_version_code, mock_tracks):
    # FIXME: Update tests
    pass

    # tracks = (tracks,) if isinstance(tracks, str) else tracks
    # google_play = GooglePlay({"type": "service_account"})
    # with mock.patch.object(google_play.api_client, "list_tracks", return_value=mock_tracks) as mock_list_tracks:
    #     build_number = google_play.get_latest_build_number("com.example.app", tracks)
    #     mock_list_tracks.assert_called_once_with("com.example.app")
    # assert build_number == expected_version_code


def test_get_latest_build_number_no_tracks():
    # FIXME: Update tests
    pass

    # google_play = GooglePlay({"type": "service_account"})
    # with mock.patch.object(google_play.api_client, "list_tracks", return_value=[]) as mock_list_tracks:
    #     with pytest.raises(GooglePlayError):
    #         google_play.get_latest_build_number("com.example.app")
    #     mock_list_tracks.assert_called_once_with("com.example.app")


@pytest.mark.parametrize("track_releases", [None, []])
def test_get_latest_build_number_no_releases(track_releases, mock_tracks):
    # FIXME: Update tests
    pass

    # mock_track = mock_tracks[0]
    # mock_track.releases = track_releases
    # google_play = GooglePlay({"type": "service_account"})
    # with mock.patch.object(google_play.api_client, "list_tracks", return_value=[mock_track]) as mock_list_tracks:
    #     with pytest.raises(GooglePlayError):
    #         google_play.get_latest_build_number("com.example.app")
    #     mock_list_tracks.assert_called_once_with("com.example.app")


@pytest.mark.parametrize("track_releases", [None, []])
def test_get_latest_build_number_no_version_codes(track_releases, mock_tracks):
    # FIXME: Update tests
    pass

    # # Production track does not have releases with version code
    # production_track = next(t for t in mock_tracks if t.track == "production")
    # google_play = GooglePlay({"type": "service_account"})
    # with mock.patch.object(
    #         google_play.api_client,
    #         "list_tracks",
    #         return_value=[production_track],
    # ) as mock_list_tracks:
    #     with pytest.raises(GooglePlayError):
    #         google_play.get_latest_build_number("com.example.app")
    #     mock_list_tracks.assert_called_once_with("com.example.app")
