from __future__ import annotations

from typing import List
from typing import Tuple
from unittest import mock

import pytest

from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import ReleaseStatus
from codemagic.google.resources.google_play import Track
from codemagic.tools import GooglePlay
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError

credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS


@pytest.mark.parametrize(
    "track_names, expected_version_code",
    [
        (("alpha",), 65),
        (("beta",), 66),
        (("internal",), 67),
        ((), 67),
        (("alpha", "production"), 65),
        (("beta", "production"), 66),
        (("internal", "production"), 67),
        (("alpha", "beta", "internal"), 67),
        (("alpha", "beta", "internal", "production"), 67),
    ],
)
def test_get_latest_build_number(track_names: Tuple[str], expected_version_code, tracks: List[Track]):
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.edits.create.return_value = mock_edit
        build_number = google_play.get_latest_build_number("com.example.app", track_names)

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")

    assert build_number == expected_version_code


def test_get_latest_build_number_no_tracks():
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = []
        mock_google_play_client.edits.create.return_value = mock_edit

        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number("com.example.app")

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")


@pytest.mark.parametrize("track_releases", [None, []])
def test_get_latest_build_number_no_releases(track_releases):
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = [Track(track="alpha", releases=track_releases)]
        mock_google_play_client.edits.create.return_value = mock_edit

        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number("com.example.app")

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")


def test_get_latest_build_number_no_version_codes():
    track_without_version_code = Track(track="production", releases=[Release(status=ReleaseStatus.DRAFT)])
    google_play = GooglePlay({"type": "service_account"})
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = [track_without_version_code]
        mock_google_play_client.edits.create.return_value = mock_edit

        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number("com.example.app")

        mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
        mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
        mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")
