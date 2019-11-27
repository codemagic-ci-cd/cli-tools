from __future__ import annotations

from datetime import datetime
from datetime import timezone

import pytest

from apple.resources import Resource


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
