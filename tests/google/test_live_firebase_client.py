import os

import pytest

from codemagic.google import FirebaseClient
from codemagic.google.resources import OrderBy


@pytest.fixture
def firebase_client(credentials):
    return FirebaseClient(credentials)


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase access')
def test_list_releases(app_identifier, credentials, firebase_client, release):
    order_by = OrderBy.CREATE_TIME_ASC
    releases = firebase_client.releases.list(app_identifier, order_by=order_by, page_size=2)

    assert releases[0] == release
    assert releases[1].buildVersion == 71


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase access')
def test_list_releases_pagination(app_identifier, credentials, firebase_client, release):
    releases = firebase_client.releases.list(app_identifier, page_size=1)

    assert releases[0].buildVersion == 71
    assert releases[1] == release
