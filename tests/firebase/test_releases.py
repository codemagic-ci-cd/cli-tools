import json
import os
from datetime import datetime
from datetime import timezone
from pathlib import Path
from unittest import mock

import pytest

from codemagic.firebase import FirebaseAPIClient
from codemagic.firebase.resource_managers.release_manager import FirebaseReleaseResourceManager
from codemagic.firebase.resource_managers.release_manager import ReleaseParentIdentifier
from codemagic.firebase.resources import ReleaseResource


@pytest.fixture
def mock_release_response_data():
    return {
        'name': 'projects/228333310124/apps/1:228333310124:ios:5e439e0d0231a788ac8f09/releases/0fam13pr3rea0',
        'releaseNotes': {'text': 'Something new :) :)'},
        'displayVersion': '0.0.42',
        'buildVersion': '70',
        'createTime': '2023-05-18T12:30:17.454581Z',
        'firebaseConsoleUri': '',
        'testingUri': '',
        'binaryDownloadUri': '',
    }


@pytest.fixture
def mock_release():
    return ReleaseResource(
        name='projects/228333310124/apps/1:228333310124:ios:5e439e0d0231a788ac8f09/releases/0fam13pr3rea0',
        releaseNotes=ReleaseResource.ReleaseNotes('Something new :) :)'),
        displayVersion='0.0.42',
        buildVersion=70,
        createTime=datetime(2023, 5, 18, 12, 30, 17, 454581, tzinfo=timezone.utc),
        firebaseConsoleUri=mock.ANY,
        testingUri=mock.ANY,
        binaryDownloadUri=mock.ANY,
    )


@pytest.fixture
def project_id():
    return '228333310124'


@pytest.fixture
def app_id():
    return '1:228333310124:ios:5e439e0d0231a788ac8f09'


@pytest.fixture
def keyfile():
    content = Path(os.environ['FIREBASE_SERVICE_ACCOUNT_PATH']).read_text()
    return json.loads(content)


@pytest.fixture
def client(keyfile):
    return FirebaseAPIClient(keyfile)


def test_release(mock_release_response_data, mock_release):
    assert ReleaseResource(**mock_release_response_data) == mock_release


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase API access')
def test_list_releases(project_id, app_id, keyfile, client, mock_release):
    order_by = FirebaseReleaseResourceManager.OrderBy.create_time_asc
    parent_identifier = ReleaseParentIdentifier(project_id, app_id)
    releases = client.releases.list(parent_identifier, order_by=order_by, page_size=2)

    assert releases[0] == mock_release
    assert releases[1].buildVersion == 71


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase API access')
def test_list_releases_pagination(project_id, app_id, keyfile, client, mock_release):
    parent_identifier = ReleaseParentIdentifier(project_id, app_id)
    releases = client.releases.list(parent_identifier, page_size=1)

    assert releases[0].buildVersion == 71
    assert releases[1] == mock_release
