from __future__ import annotations

from datetime import datetime
from datetime import timezone

import pytest

from codemagic_cli_tools.apple.resources import *
from codemagic_cli_tools.apple.resources import Resource


@pytest.mark.parametrize('iso_8601_timestamp, expected_datetime', [
    (None, None),
    (datetime(2020, 8, 4, 11, 44, 12, tzinfo=timezone.utc), '2020-08-04T11:44:12.000+0000'),
    (datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), '1970-01-01T00:00:00.000+0000'),
])
def test_to_iso_8601(iso_8601_timestamp, expected_datetime):
    assert Resource.to_iso_8601(iso_8601_timestamp) == expected_datetime


@pytest.mark.parametrize('given_datetime, expected_iso_8601_timestamp', [
    (None, None),
    ('2020-08-04T11:44:12.000+0000', datetime(2020, 8, 4, 11, 44, 12, tzinfo=timezone.utc)),
    ('1970-01-01T00:00:00.000+0000', datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
])
def test_from_iso_8601(given_datetime, expected_iso_8601_timestamp):
    assert Resource.from_iso_8601(given_datetime) == expected_iso_8601_timestamp


def test_resource_tabular_formatting(api_profile):
    expected_format = \
        'Id: 253YPL8VY6\n' \
        'Type: profiles\n' \
        'Name: test profile\n' \
        'Platform: IOS\n' \
        'Uuid: 55b8fdb4-b7d2-402d-b48b-2523f7b9c384\n' \
        'Created date: 2019-11-29 13:56:50.220000+00:00\n' \
        'State: ACTIVE\n' \
        'Type: IOS_APP_DEVELOPMENT\n' \
        'Expiration date: 2020-11-28 13:56:50.220000+00:00\n' \
        'Content: "..."'
    assert str(Profile(api_profile)) == expected_format
