import argparse
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from codemagic.cli.argument import CommonArgumentTypes


@pytest.mark.parametrize('timestamp, expected', (
    ('2020-08-04T11:44:12.000+0000', datetime(2020, 8, 4, 11, 44, 12, tzinfo=timezone.utc)),
    ('2021-01-28T06:01:32-08:00', datetime(2021, 1, 28, 6, 1, 32, tzinfo=timezone(timedelta(hours=-8)))),
    ('2021-11-24T14:03:01+00:00', datetime(2021, 11, 24, 14, 3, 1, tzinfo=timezone.utc)),
    ('2021-11-24T14:03:01Z', datetime(2021, 11, 24, 14, 3, 1, tzinfo=timezone.utc)),
    ('20211124T140301Z', datetime(2021, 11, 24, 14, 3, 1, tzinfo=timezone.utc)),
    ('20211124T140301+02:00', datetime(2021, 11, 24, 14, 3, 1, tzinfo=timezone(timedelta(hours=2)))),
))
def test_iso_8601_datetime(timestamp, expected):
    dt = CommonArgumentTypes.iso_8601_datetime(timestamp)
    assert dt == expected


@pytest.mark.parametrize('invalid_timestamp', (
    'not a timestamp',  # Gibberish
    '2021-11-10T14:55:41',
    '20211124T140301',
))
def test_invalid_iso_8601_datetime(invalid_timestamp):
    with pytest.raises(argparse.ArgumentTypeError) as error_info:
        CommonArgumentTypes.iso_8601_datetime(invalid_timestamp)
    assert str(error_info.value) == f'"{invalid_timestamp}" is not a valid ISO 8601 timestamp'
