from datetime import datetime

import pytz
from freezegun import freeze_time
from lilya.contrib.security.utils import convert_time

from ravyn.parsers import flatten


@freeze_time("2023-01-01 18:05:20")
def test_convert_time():
    now = datetime.now()

    time = convert_time(now)

    assert time is not None
    assert isinstance(time, datetime)
    assert time.tzinfo is None


@freeze_time("2023-01-01 18:05:20")
def test_convert_time_tz_info():
    now = datetime.now(tz=pytz.timezone("Europe/Rome"))

    time = convert_time(now)

    assert time is not None
    assert isinstance(time, datetime)
    assert str(time.tzinfo) == "Europe/Rome"


def test_flatten():
    data = [1, [2], [3, [4, [5]], [[[[[6]]]]]]]

    flatten_data = flatten(data)

    assert flatten_data == [1, 2, 3, 4, 5, 6]
