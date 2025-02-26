from __future__ import annotations

import dataclasses
from typing import List
from typing import Tuple
from unittest import mock

import pytest

from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import Status
from codemagic.google.resources.google_play import Track
from codemagic.tools import GooglePlay
from codemagic.tools.google_play.errors import GooglePlayError


@pytest.fixture
def version_codes_track() -> Track:
    return Track(
        track="internal",
        releases=[
            Release(
                status=Status.DRAFT,
                name="29 (1.0.29)",
                versionCodes=["29"],
            ),
            Release(
                status=Status.COMPLETED,
                name="26 (1.0.26)",
                versionCodes=["26"],
            ),
        ],
    )


@pytest.fixture
def google_play() -> GooglePlay:
    return GooglePlay(credentials={"type": "service_account"})


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
def test_get_latest_build_number(
    track_names: Tuple[str],
    expected_version_code: int,
    google_play: GooglePlay,
    tracks: List[Track],
):
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.edits.create.return_value = mock_edit
        build_number = google_play.get_latest_build_number("com.example.app", track_names)

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")

    assert build_number == expected_version_code


def test_get_latest_build_number_no_tracks(google_play: GooglePlay):
    edit = AppEdit(id="mock-edit-id", expiryTimeSeconds="10")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = []
        mock_google_play_client.edits.create.return_value = edit

        with pytest.raises(GooglePlayError) as exc_info:
            google_play.get_latest_build_number("com.example.app")

    assert str(exc_info.value) == 'Version code info is missing from all tracks for package "com.example.app"'
    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(edit, package_name="com.example.app")


@pytest.mark.parametrize("track_releases", [None, []])
def test_get_latest_build_number_no_releases(track_releases, google_play: GooglePlay):
    edit = AppEdit(id="mock-edit-id", expiryTimeSeconds="10")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = [Track(track="alpha", releases=track_releases)]
        mock_google_play_client.edits.create.return_value = edit

        with pytest.raises(GooglePlayError) as exc_info:
            google_play.get_latest_build_number("com.example.app")

    assert str(exc_info.value) == 'Version code info is missing from all tracks for package "com.example.app"'
    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(edit, package_name="com.example.app")


def test_get_latest_build_number_no_version_codes(google_play: GooglePlay):
    track_without_version_code = Track(track="production", releases=[Release(status=Status.DRAFT)])
    edit = AppEdit(id="mock-edit-id", expiryTimeSeconds="10")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = [track_without_version_code]
        mock_google_play_client.edits.create.return_value = edit

        with pytest.raises(GooglePlayError) as exc_info:
            google_play.get_latest_build_number("com.example.app")

        assert str(exc_info.value) == 'Version code info is missing from all tracks for package "com.example.app"'
        mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
        mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
        mock_google_play_client.edits.delete.assert_called_once_with(edit, package_name="com.example.app")


def test_get_max_version_code(google_play: GooglePlay, version_codes_track: Track):
    max_version_code = google_play.get_max_version_code(version_codes_track)
    assert max_version_code == 29


@pytest.mark.parametrize("empty_releases", [None, []])
def test_get_max_version_code_no_releases(
    empty_releases,
    google_play: GooglePlay,
    version_codes_track: Track,
):
    track = dataclasses.replace(version_codes_track, releases=empty_releases)
    with pytest.raises(ValueError) as exc_info:
        google_play.get_max_version_code(track)
    expected_error = 'Failed to get version code from "internal" track: track has no releases'
    assert str(exc_info.value) == expected_error


@pytest.mark.parametrize("empty_version_codes", [None, []])
def test_get_max_version_code_no_version_codes(
    empty_version_codes,
    google_play: GooglePlay,
    version_codes_track: Track,
):
    track = dataclasses.replace(
        version_codes_track,
        releases=[
            dataclasses.replace(release, versionCodes=empty_version_codes) for release in version_codes_track.releases
        ],
    )
    with pytest.raises(ValueError) as exc_info:
        google_play.get_max_version_code(track)
    expected_error = 'Failed to get version code from "internal" track: releases with version code do not exist'
    assert str(exc_info.value) == expected_error
