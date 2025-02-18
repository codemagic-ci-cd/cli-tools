import json
import os
from pathlib import Path

import pytest

from codemagic.google import GooglePlayClient
from codemagic.google.resources.google_play import LocalizedText
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import ReleaseStatus
from codemagic.google.resources.google_play import Track


@pytest.fixture(scope="module")
def google_play_client() -> GooglePlayClient:
    if "TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_PATH" in os.environ:
        credentials_path = Path(os.environ["TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_PATH"])
        credentials = credentials_path.expanduser().read_text()
    elif "TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_CONTENT" in os.environ:
        credentials = os.environ["TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_CONTENT"]
    else:
        raise KeyError(
            "TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_PATH",
            "TEST_GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS_CONTENT",
        )
    google_play_service_account_credentials = json.loads(credentials)
    return GooglePlayClient(google_play_service_account_credentials)


@pytest.mark.skipif(not os.environ.get("RUN_LIVE_API_TESTS"), reason="Live Google Play Developer API access")
def test_list_tracks(google_play_client: GooglePlayClient):
    package_name = "io.codemagic.cli_tools_google_play"
    edit = google_play_client.edits.create(package_name)
    tracks = google_play_client.tracks.list(package_name, edit.id)
    google_play_client.edits.delete(edit, package_name)
    track_names = {t.track for t in tracks}
    assert track_names == {"production", "beta", "alpha", "internal"}


@pytest.mark.skipif(not os.environ.get("RUN_LIVE_API_TESTS"), reason="Live Google Play Developer API access")
def test_get_track(google_play_client: GooglePlayClient):
    package_name = "io.codemagic.cli_tools_google_play"
    edit = google_play_client.edits.create(package_name)
    track = google_play_client.tracks.get(
        package_name=package_name,
        track_name="alpha",
        edit_id=edit.id,
    )
    google_play_client.edits.delete(edit, package_name)
    assert track == Track(
        track="alpha",
        releases=[
            Release(
                status=ReleaseStatus.COMPLETED,
                name="5 (1.0)",
                versionCodes=["5"],
                releaseNotes=[
                    LocalizedText(
                        language="en-US",
                        text="5th release",
                    ),
                ],
            ),
        ],
    )
