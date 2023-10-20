from __future__ import annotations

import dataclasses

import pytest
from codemagic.google_play.resources import Release
from codemagic.google_play.resources import ReleaseStatus
from codemagic.google_play.resources import Track
from codemagic.google_play.resources.track import CountryTargeting
from codemagic.google_play.resources.track import LocalizedText


def test_track_initialization(api_track):
    track = Track(**api_track)
    assert track.dict() == api_track


def test_max_version_code(api_track):
    track = Track(**api_track)
    assert track.get_max_version_code() == 29


def test_max_version_code_error_no_releases(api_track):
    api_track.pop("releases")
    track = Track(**api_track)
    with pytest.raises(ValueError) as e:
        track.get_max_version_code()
    assert str(e.value) == 'Failed to get version code from "internal" track: track has no releases'


def test_max_version_code_error_no_version_codes(api_track):
    for release in api_track["releases"]:
        release.pop("versionCodes")
    track = Track(**api_track)
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
