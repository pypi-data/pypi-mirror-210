from datetime import datetime, timedelta
from typing import Generator, Optional, Tuple, Union

from dateutil.parser import parse


def ensure_datetime(value: Optional[Union[str, datetime]]):
    if value is None:
        return value

    if isinstance(value, datetime):
        return value

    return parse(value)


def datetime_range(
    start: Optional[datetime], end: Optional[datetime], step: timedelta
) -> Generator[Tuple[Optional[datetime], Optional[datetime]], None, None]:
    if start is None or end is None:
        yield None, None
        return

    curr = start
    while curr <= end:
        yield curr, min(curr + step, end)
        curr += step
