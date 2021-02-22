from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from codemagic.apple.resources import Profile
from codemagic.apple.resources import Resource
from codemagic.apple.resources.resource import PrettyNameMeta


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
    ('2021-01-28T06:01:32-08:00', datetime(2021, 1, 28, 6, 1, 32, tzinfo=timezone(timedelta(days=-1, seconds=57600)))),
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


@pytest.mark.parametrize('class_name, pretty_name', [
    ('BundleId', 'Bundle ID'),
    ('RandomNameWithIdInIt', 'Random Name With ID In It'),
    ('Resource', 'Resource'),
])
def test_pretty_name_meta(class_name, pretty_name):
    class K(metaclass=PrettyNameMeta):
        def dict(self):
            return {}

    K.__name__ = class_name
    assert str(K) == pretty_name


@pytest.mark.parametrize('class_name, pretty_name', [
    ('BundleId', 'Bundle ID'),
    ('RandomNameWithIdInIt', 'Random Name With ID In It'),
    ('Resource', 'Resource'),
    ('name', 'name'),
])
def test_pretty_name(class_name, pretty_name):
    class K(metaclass=PrettyNameMeta):
        ...

    K.__name__ = class_name
    assert str(K) == pretty_name
    assert K.plural(1) == pretty_name


@pytest.mark.parametrize('class_name, plural_name', [
    ('Capability', 'Capabilities'),
    ('Resource', 'Resources'),
    ('name', 'names'),
    ('BundleId', 'Bundle IDs'),
])
def test_pretty_name_plural(class_name, plural_name):
    class K(metaclass=PrettyNameMeta):
        ...

    K.__name__ = class_name
    assert K.plural() == plural_name
    assert K.s == plural_name
