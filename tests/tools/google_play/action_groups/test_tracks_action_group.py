from __future__ import annotations

from typing import List
from unittest import mock

from codemagic.google.resources.google_play import Track
from codemagic.tools import GooglePlay
from codemagic.tools.google_play.arguments import GooglePlayArgument

credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS


def test_get_track(track: Track):
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.get.return_value = track
        mock_google_play_client.edits.create.return_value = mock_edit
        track = google_play.get_track("com.example.app", track.track)

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.get.assert_called_once_with("com.example.app", track.track, "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")
    assert track == track


def test_list_tracks(tracks: List[Track]):
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.edits.create.return_value = mock_edit
        tracks = google_play.list_tracks("com.example.app")

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")

    assert tracks == tracks
