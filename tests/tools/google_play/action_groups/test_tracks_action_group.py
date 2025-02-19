from __future__ import annotations

from typing import List
from unittest import mock

import pytest

from codemagic.google.resources.google_play import CountryTargeting
from codemagic.google.resources.google_play import Edit
from codemagic.google.resources.google_play import LocalizedText
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import ReleaseStatus
from codemagic.google.resources.google_play import Track
from codemagic.tools import GooglePlay
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError

credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS


def test_get_track():
    track = Track(
        track="alpha",
        releases=[
            Release(
                status=ReleaseStatus.COMPLETED,
                name="1.0",
                userFraction=0.5,
                countryTargeting=CountryTargeting(
                    countries=["EE", "EN"],
                    includeRestOfWorld=False,
                ),
                inAppUpdatePriority=2,
                versionCodes=["1", "2"],
                releaseNotes=[
                    LocalizedText(
                        language="en-GB",
                        text="Release note",
                    ),
                    LocalizedText(
                        language="et-EE",
                        text="Uue versiooni märkmed",
                    ),
                ],
            ),
            Release(
                status=ReleaseStatus.STATUS_UNSPECIFIED,
            ),
        ],
    )
    google_play = GooglePlay({"type": "service_account"})
    edit = Edit(id="mock-edit-id", expiryTimeSeconds="10")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.get.return_value = track
        mock_google_play_client.edits.create.return_value = edit
        track = google_play.get_track("com.example.app", track.track)

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.get.assert_called_once_with("com.example.app", track.track, "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(edit, package_name="com.example.app")
    assert track == track


def test_list_tracks(tracks: List[Track]):
    google_play = GooglePlay({"type": "service_account"})
    edit = Edit(id="mock-edit-id", expiryTimeSeconds="10")

    with mock.patch.object(google_play, "client") as mock_google_play_client:
        mock_google_play_client.tracks.list.return_value = tracks
        mock_google_play_client.edits.create.return_value = edit
        tracks = google_play.list_tracks("com.example.app")

    mock_google_play_client.edits.create.assert_called_once_with(package_name="com.example.app")
    mock_google_play_client.tracks.list.assert_called_once_with("com.example.app", "mock-edit-id")
    mock_google_play_client.edits.delete.assert_called_once_with(edit, package_name="com.example.app")

    assert tracks == tracks


@pytest.mark.parametrize("empty_releases", (None, [], ()))
def test_promote_release_no_source_releases(empty_releases):
    google_play = GooglePlay({"type": "service_account"})
    with mock.patch.object(google_play, "get_track") as mock_get_track:
        mock_get_track.side_effect = [
            Track(track="alpha", releases=empty_releases),
            Track(track="beta"),
        ]
        with pytest.raises(GooglePlayError) as exc_info:
            google_play.promote_release(
                package_name="com.example.app",
                source_track_name="alpha",
                target_track_name="beta",
            )

    assert str(exc_info.value) == 'Source track "alpha" does not have any releases'


def test_promote_release():
    google_play = GooglePlay({"type": "service_account"})
    edit = Edit(id="mock-edit-id", expiryTimeSeconds="10")
    source_track = Track(
        track="alpha",
        releases=[
            Release(
                status=ReleaseStatus.DRAFT,
                name="1.2.3",
                versionCodes=["1", "2"],
                countryTargeting=CountryTargeting(
                    countries=["EE", "EN"],
                ),
            ),
        ],
    )
    target_track = Track(track="beta")
    expected_updated_track = Track(
        track="beta",
        releases=[
            Release(
                status=ReleaseStatus.IN_PROGRESS,
                name="1.2.3",
                versionCodes=["1", "2"],
                countryTargeting=CountryTargeting(
                    countries=["EE", "EN"],
                ),
                userFraction=0.7,
            ),
        ],
    )

    with mock.patch.object(google_play, "client") as mock_google_play_client, mock.patch.object(
        google_play,
        "get_track",
    ) as mock_get_track:
        mock_google_play_client.edits.create.return_value = edit
        mock_google_play_client.tracks.update.return_value = expected_updated_track
        mock_get_track.side_effect = [source_track, target_track]

        updated_track = google_play.promote_release(
            package_name="com.example.app",
            source_track_name="alpha",
            target_track_name="beta",
            promoted_status=ReleaseStatus.IN_PROGRESS,
            promoted_user_fraction=0.7,
        )

    mock_google_play_client.edits.create.assert_called_once_with("com.example.app")
    mock_google_play_client.tracks.update.assert_called_once_with(expected_updated_track, "com.example.app", edit.id)
    mock_google_play_client.edits.commit.assert_called_once_with(edit, "com.example.app")
    assert updated_track == expected_updated_track
