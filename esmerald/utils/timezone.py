"""
Timezone-related classes and functions.
"""
import functools
import sys
from typing import Any, Optional, Union
from zoneinfo import ZoneInfo

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from datetime import date, datetime, timedelta, timezone

from asgiref.local import Local
from esmerald.conf import settings

__all__ = [
    "utc",
    "get_fixed_timezone",
    "get_default_timezone",
    "get_default_timezone_name",
    "get_current_timezone",
    "get_current_timezone_name",
    "localtime",
    "localdate",
    "now",
    "is_aware",
    "is_naive",
    "make_aware",
    "make_naive",
]

NOT_PASSED = object()


def __getattr__(name: str) -> timezone.utc:
    if name != "utc":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return timezone.utc


def get_fixed_timezone(offset: Any) -> timezone:
    """Return a tzinfo instance with a fixed offset from UTC."""
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = "-" if offset < 0 else "+"
    hhmm = "%02d%02d" % divmod(abs(offset), 60)
    name = sign + hhmm
    return timezone(timedelta(minutes=offset), name)


# In order to avoid accessing settings at compile time,
# wrap the logic in a function and cache the result.


@functools.lru_cache
def get_default_timezone() -> ZoneInfo:
    """
    Return the default time zone as a tzinfo instance.

    This is the time zone defined by settings.timezone.
    """
    return zoneinfo.ZoneInfo(settings.timezone)


# This function exists for consistency with get_current_timezone_name
def get_default_timezone_name() -> str:
    """Return the name of the default time zone."""
    return _get_timezone_name(get_default_timezone())


_active = Local()


def get_current_timezone() -> ZoneInfo:
    """Return the currently active time zone as a tzinfo instance."""
    return getattr(_active, "value", get_default_timezone())


def get_current_timezone_name() -> str:
    """Return the name of the currently active time zone."""
    return _get_timezone_name(get_current_timezone())


def _get_timezone_name(timezone: timezone) -> Union[timezone, str]:
    """
    Return the offset for fixed offset timezones, or the name of timezone if
    not set.
    """
    return timezone.tzname(None) or str(timezone)


# Utilities


def localtime(value=None, timezone=None) -> Union[datetime, Any]:
    """
    Convert an aware datetime.datetime to local time.

    Only aware datetimes are allowed. When value is omitted, it defaults to
    now().

    Local time is defined by the current time zone, unless another time zone
    is specified.
    """
    if value is None:
        value = now()
    if timezone is None:
        timezone = get_current_timezone()
    # Emulate the behavior of astimezone() on Python < 3.6.
    if is_naive(value):
        raise ValueError("localtime() cannot be applied to a naive datetime")
    return value.astimezone(timezone)


def localdate(value=None, timezone=None) -> date:
    """
    Convert an aware datetime to local time and return the value's date.

    Only aware datetimes are allowed. When value is omitted, it defaults to
    now().

    Local time is defined by the current time zone, unless another time zone is
    specified.
    """
    return localtime(value, timezone).date()


def now() -> datetime:
    """
    Return an aware or naive datetime.datetime, depending on settings.use_tz.
    """
    return datetime.now(tz=timezone.utc if settings.use_tz else None)


# By design, these four functions don't perform any checks on their arguments.
# The caller should ensure that they don't receive an invalid value like None.


def is_aware(value: datetime) -> Union[timedelta, None]:
    """
    Determine if a given datetime.datetime is aware.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def is_naive(value: datetime) -> Union[timedelta, None]:
    """
    Determine if a given datetime.datetime is naive.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is None


def make_aware(value, timezone: Optional[timezone] = None, is_dst=NOT_PASSED):
    """Make a naive datetime.datetime in a given time zone aware."""
    if is_dst is NOT_PASSED:
        is_dst = None

    if timezone is None:
        timezone = get_current_timezone()
    if _is_pytz_zone(timezone):
        # This method is available for pytz time zones.
        return timezone.localize(value, is_dst=is_dst)
    else:
        # Check that we won't overwrite the timezone of an aware datetime.
        if is_aware(value):
            raise ValueError("make_aware expects a naive datetime, got %s" % value)
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)


def make_naive(value, timezone=None):
    """Make an aware datetime.datetime naive in a given time zone."""
    if timezone is None:
        timezone = get_current_timezone()
    # Emulate the behavior of astimezone() on Python < 3.6.
    if is_naive(value):
        raise ValueError("make_naive() cannot be applied to a naive datetime")
    return value.astimezone(timezone).replace(tzinfo=None)


_PYTZ_IMPORTED = False


def _pytz_imported() -> bool:
    """
    Detects whether or not pytz has been imported without importing pytz.

    Copied from pytz_deprecation_shim with thanks to Paul Ganssle.
    """
    global _PYTZ_IMPORTED

    if not _PYTZ_IMPORTED and "pytz" in sys.modules:
        _PYTZ_IMPORTED = True

    return _PYTZ_IMPORTED


def _is_pytz_zone(tz) -> Any:
    """Checks if a zone is a pytz zone."""
    # See if pytz was already imported rather than checking
    # settings.USE_DEPRECATED_PYTZ to *allow* manually passing a pytz timezone,
    # which some of the test cases (at least) rely on.
    if not _pytz_imported():
        return False

    # If tz could be pytz, then pytz is needed here.
    import pytz

    _PYTZ_BASE_CLASSES = (pytz.tzinfo.BaseTzInfo, pytz._FixedOffset)
    # In releases prior to 2018.4, pytz.UTC was not a subclass of BaseTzInfo
    if not isinstance(pytz.UTC, pytz._FixedOffset):
        _PYTZ_BASE_CLASSES = _PYTZ_BASE_CLASSES + (type(pytz.UTC),)

    return isinstance(tz, _PYTZ_BASE_CLASSES)


_DIR = dir()


def __dir__():
    return sorted([*_DIR, "utc"])
