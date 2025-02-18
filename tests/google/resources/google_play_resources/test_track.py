from __future__ import annotations

import dataclasses

import pytest

from codemagic.google.resources.google_play import CountryTargeting
from codemagic.google.resources.google_play import LocalizedText
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import ReleaseStatus
from codemagic.google.resources.google_play import Track


def test_track_initialization(api_google_play_track: dict):
    track = Track(**api_google_play_track)
    assert track.dict() == api_google_play_track


def test_max_version_code(api_google_play_track: dict):
    track = Track(**api_google_play_track)
    assert track.get_max_version_code() == 29


def test_max_version_code_error_no_releases(api_google_play_track: dict):
    api_google_play_track.pop("releases")
    track = Track(**api_google_play_track)
    with pytest.raises(ValueError) as e:
        track.get_max_version_code()
    assert str(e.value) == 'Failed to get version code from "internal" track: track has no releases'


def test_max_version_code_error_no_version_codes(api_google_play_track: dict):
    for release in api_google_play_track["releases"]:
        release.pop("versionCodes")
    track = Track(**api_google_play_track)
    with pytest.raises(ValueError) as e:
        track.get_max_version_code()
    assert str(e.value) == 'Failed to get version code from "internal" track: releases with version code do not exist'


def test_release():
    release = Release(
        **{
            "name": "1.2.3",
            "versionCodes": ["123"],
            "releaseNotes": [{"language": "en-US", "text": "* Release\n\nnotes"}],
            "status": "draft",
        },
    )

    assert release.name == "1.2.3"
    assert release.versionCodes == ["123"]
    assert release.releaseNotes == [LocalizedText(language="en-US", text="* Release\n\nnotes")]
    assert release.status is ReleaseStatus.DRAFT
    assert release.countryTargeting is None

    updated_release = dataclasses.replace(
        release,
        status=ReleaseStatus.COMPLETED,
        countryTargeting={"countries": ["EE", "GB"], "includeRestOfWorld": False},  # type: ignore
    )

    assert updated_release.name == release.name
    assert updated_release.versionCodes == release.versionCodes
    assert updated_release.releaseNotes == release.releaseNotes
    assert updated_release.status is ReleaseStatus.COMPLETED
    assert updated_release.countryTargeting == CountryTargeting(countries=["EE", "GB"], includeRestOfWorld=False)


def test_track_string_representation(api_google_play_track: dict):
    track = Track(**api_google_play_track)
    expected_output = (
        "Track: internal\n"
        "Releases:\n"
        "    - Status: draft\n"
        "      Name: 29 (1.0.29)\n"
        "      Version codes:\n"
        "          - 29\n"
        "    - Status: completed\n"
        "      Name: trying2\n"
        "      Version codes:\n"
        "          - 26\n"
        "      Release notes:\n"
        "          - Language: en-US\n"
        "            Text: trying2"
    )
    assert str(track) == expected_output
