from __future__ import annotations

from codemagic.tools.google_play.arguments import GooglePlayArgument

credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS


def test_get_track(mock_tracks):
    # FIXME: Update tests
    pass
    # google_play = GooglePlay({"type": "service_account"})
    # mock_track = mock_tracks[0]
    # with mock.patch.object(google_play.client, "get_track", return_value=mock_track) as mock_get_track:
    #     track = google_play.get_track("com.example.app", mock_track.track)
    #     mock_get_track.assert_called_once_with("com.example.app", mock_track.track)
    # assert track == mock_track


def test_list_tracks(mock_tracks):
    # FIXME: Update tests
    pass
    # google_play = GooglePlay({"type": "service_account"})
    # with mock.patch.object(google_play.api_client, "list_tracks", return_value=mock_tracks) as mock_list_tracks:
    #     tracks = google_play.list_tracks("com.example.app")
    #     mock_list_tracks.assert_called_once_with("com.example.app")
    # assert tracks == mock_tracks
