from __future__ import annotations

import pytest

from codemagic.google_play.resources import Track


def test_track_initialization(api_track):
    track = Track(**api_track)
    assert track.dict() == api_track


def test_max_version_code(api_track):
    track = Track(**api_track)
    assert track.get_max_version_code() == 29


def test_max_version_code_error_no_releases(api_track):
    api_track.pop('releases')
    track = Track(**api_track)
    with pytest.raises(ValueError) as e:
        track.get_max_version_code()
    assert 'No release information' in str(e.value)


def test_max_version_code_error_no_version_codes(api_track):
    for release in api_track['releases']:
        release.pop('versionCodes')
    track = Track(**api_track)
    with pytest.raises(ValueError) as e:
        track.get_max_version_code()
    assert 'No releases with uploaded App bundles or APKs' in str(e.value)
