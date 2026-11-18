from __future__ import annotations

import dataclasses
from typing import List
from typing import Tuple
from unittest import mock

import pytest

from codemagic.google.resources.google_play import Apk
from codemagic.google.resources.google_play import ApkBinary
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Bundle
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
    return GooglePlay({"type": "service_account"})


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


def _bundle(version_code: int) -> Bundle:
    return Bundle(versionCode=version_code, sha1="sha1", sha256="sha256")


def _apk(version_code: int) -> Apk:
    return Apk(versionCode=version_code, binary=ApkBinary(sha1="sha1", sha256="sha256"))


def test_get_latest_build_number_does_not_list_uploaded_builds_by_default(
    google_play: GooglePlay,
    tracks: List[Track],
):
    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.edits.create.return_value = mock.MagicMock(id="mock-edit-id")
        google_play.get_latest_build_number("com.example.app")

    mock_google_play_client.bundles.list.assert_not_called()
    mock_google_play_client.apks.list.assert_not_called()


@pytest.mark.parametrize(
    "bundles, apks, expected_version_code",
    [
        ([_bundle(70)], [], 70),
        ([], [_apk(71)], 71),
        ([_bundle(70)], [_apk(68)], 70),
        ([_bundle(60)], [_apk(61)], 67),
        ([], [], 67),
    ],
)
def test_get_latest_build_number_include_uploaded_builds(
    bundles: List[Bundle],
    apks: List[Apk],
    expected_version_code: int,
    google_play: GooglePlay,
    tracks: List[Track],
):
    mock_edit = mock.MagicMock(id="mock-edit-id")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.bundles.list.return_value = bundles
        mock_google_play_client.apks.list.return_value = apks
        mock_google_play_client.edits.create.return_value = mock_edit
        build_number = google_play.get_latest_build_number("com.example.app", include_uploaded_builds=True)

    assert build_number == expected_version_code
    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.bundles.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.apks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(mock_edit, package_name="com.example.app")


def test_get_latest_build_number_include_uploaded_builds_without_tracks(google_play: GooglePlay):
    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = []
        mock_google_play_client.bundles.list.return_value = [_bundle(12), _bundle(15)]
        mock_google_play_client.apks.list.return_value = []
        mock_google_play_client.edits.create.return_value = AppEdit(id="mock-edit-id", expiryTimeSeconds="10")
        build_number = google_play.get_latest_build_number("com.example.app", include_uploaded_builds=True)

    assert build_number == 15


def test_get_latest_build_number_include_uploaded_builds_nothing_found(google_play: GooglePlay):
    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = []
        mock_google_play_client.bundles.list.return_value = []
        mock_google_play_client.apks.list.return_value = []
        mock_google_play_client.edits.create.return_value = AppEdit(id="mock-edit-id", expiryTimeSeconds="10")

        with pytest.raises(GooglePlayError) as exc_info:
            google_play.get_latest_build_number("com.example.app", include_uploaded_builds=True)

    expected_error = 'Version code info is missing from all tracks and uploaded builds for package "com.example.app"'
    assert str(exc_info.value) == expected_error


def test_get_latest_build_number_include_uploaded_builds_with_tracks(google_play: GooglePlay):
    with mock.patch.object(google_play, "client") as mock_google_play_client:
        with pytest.raises(GooglePlayError) as exc_info:
            google_play.get_latest_build_number("com.example.app", ["production"], include_uploaded_builds=True)

    assert str(exc_info.value) == "Uploaded builds can only be included when no tracks are specified"
    mock_google_play_client.edits.create.assert_not_called()
