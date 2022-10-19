from datetime import datetime, timezone


def convert_time(date: datetime) -> datetime:
    """
    Converts the date into a UTC compatible format.
    """
    if date.tzinfo is not None:
        date.astimezone(timezone.utc)
    return date.replace(microsecond=0)
