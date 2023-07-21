from datetime import datetime
from zoneinfo import ZoneInfo

from freezegun import freeze_time

from esmerald.security.utils import convert_time


@freeze_time("2023-01-01 18:05:20")
def test_convert_time():
    now = datetime.now()

    time = convert_time(now)

    assert time is not None
    assert isinstance(time, datetime)
    assert time.tzinfo is None


@freeze_time("2023-01-01 18:05:20")
def test_convert_time_tz_info():
    now = datetime.now(tz=ZoneInfo("Europe/Rome"))

    time = convert_time(now)

    assert time is not None
    assert isinstance(time, datetime)
    assert str(time.tzinfo) == "Europe/Rome"
