from datetime import datetime, timezone
from typing import Optional, Tuple


def convert_time(date: datetime) -> datetime:
    """
    Converts the date into a UTC compatible format.
    """
    if date.tzinfo is not None:
        date.astimezone(timezone.utc)
    return date.replace(microsecond=0)


def get_authorization_scheme_param(
    authorization_header_value: Optional[str],
) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param
