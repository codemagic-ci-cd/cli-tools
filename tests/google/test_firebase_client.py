from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
from codemagic.google import FirebaseClient
from codemagic.google.errors import GoogleCredentialsError
from codemagic.google.resource_managers import ReleaseManager
from codemagic.google.resources import OrderBy
from codemagic.google.resources import Release


def test_release(release_response, release):
    assert Release(**release_response) == release


@pytest.mark.parametrize(
    "credentials",
    [
        {},
        {"type": "service_account"},
        {"type": "service_account", "client_email": "user@example.com"},
        {
            "type": "service_account",
            "client_email": "user@example.com",
            "client_id": "client-id",
            "private_key": "invalid-private-key",
            "private_key_id": "private-key-id",
        },
    ],
)
def test_invalid_credentials(credentials, app_identifier):
    with pytest.raises(GoogleCredentialsError):
        FirebaseClient(credentials).releases.list(app_identifier)


@pytest.fixture(scope="module")
def firebase_client():
    with patch.object(FirebaseClient, "google_resource", new_callable=PropertyMock) as mock_firebase_app_distribution:
        mock_firebase_app_distribution.return_value = None
        yield FirebaseClient({})


@pytest.fixture
def mock_releases(release_response):
    release_0 = release_response.copy()
    release_1 = release_response.copy()
    release_1["buildVersion"] = "71"
    with patch.object(ReleaseManager, "_releases", new_callable=PropertyMock) as mock_resource:
        google_request_mock_class = MagicMock()
        google_request_mock_class.execute.return_value = {"releases": [release_0, release_1]}
        google_resource_mock_class = MagicMock()
        google_resource_mock_class.list.return_value = google_request_mock_class
        mock_resource.return_value = google_resource_mock_class
        yield mock_resource


def test_list_releases(app_identifier, firebase_client, release, mock_releases):
    order_by = OrderBy.CREATE_TIME_ASC
    releases = firebase_client.releases.list(app_identifier, order_by=order_by, page_size=2)

    assert releases[0] == release
    assert releases[1].buildVersion == 71


def test_list_releases_limit(app_identifier, firebase_client, mock_releases):
    releases = firebase_client.releases.list(app_identifier, limit=1)

    assert len(releases) == 1


@pytest.fixture
def mock_releases_pagination(release_response):
    release_0 = release_response.copy()
    release_1 = release_response.copy()
    release_1["buildVersion"] = "71"
    with patch.object(ReleaseManager, "_releases", new_callable=PropertyMock) as mock_resource:
        google_request_mock_class = MagicMock()
        google_request_mock_class.execute.side_effect = [
            {"releases": [release_0], "nextPageToken": "next-page-token"},
            {"releases": [release_1]},
        ]
        google_resource_mock_class = MagicMock()
        google_resource_mock_class.list.return_value = google_request_mock_class
        mock_resource.return_value = google_resource_mock_class
        yield mock_resource


def test_list_releases_pagination(app_identifier, release, firebase_client, mock_releases_pagination):
    releases = firebase_client.releases.list(app_identifier, page_size=1)

    assert len(releases) == 2
    assert releases[0] == release
    assert releases[1].buildVersion == 71
