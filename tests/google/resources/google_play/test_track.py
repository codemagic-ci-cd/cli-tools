from __future__ import annotations

import dataclasses

from codemagic.google.resources.google_play import CountryTargeting
from codemagic.google.resources.google_play import LocalizedText
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import Status
from codemagic.google.resources.google_play import Track


def test_track_initialization(api_google_play_track: dict):
    track = Track(**api_google_play_track)
    assert track.dict() == api_google_play_track


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
    assert release.status is Status.DRAFT
    assert release.countryTargeting is None

    updated_release = dataclasses.replace(
        release,
        status=Status.COMPLETED,
        countryTargeting={"countries": ["EE", "GB"], "includeRestOfWorld": False},  # type: ignore
    )

    assert updated_release.name == release.name
    assert updated_release.versionCodes == release.versionCodes
    assert updated_release.releaseNotes == release.releaseNotes
    assert updated_release.status is Status.COMPLETED
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


def test_release_with_empty_release_notes():
    release = Release(
        **{
            "name": "1.2.3",
            "versionCodes": ["123"],
            "releaseNotes": [{"language": "en-US"}],
            "status": "draft",
        },
    )

    assert release.name == "1.2.3"
    assert release.versionCodes == ["123"]
    assert release.releaseNotes == [LocalizedText(language="en-US", text="")]
    assert release.status is Status.DRAFT
