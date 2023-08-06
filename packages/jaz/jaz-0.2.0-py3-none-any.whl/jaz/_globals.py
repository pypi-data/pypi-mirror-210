from __future__ import annotations

import datetime
import zoneinfo
from typing import Any
from typing import Callable
from typing import NoReturn
from typing import Optional


def now(timezone: Optional[str] = None) -> datetime.datetime:
    utc_ts = datetime.datetime.now(datetime.timezone.utc)
    if timezone:
        tzinfo = zoneinfo.ZoneInfo(timezone)
    else:
        tzinfo = None
    tz_ts = utc_ts.astimezone(tzinfo)
    return tz_ts


def raise_helper(msg: str) -> NoReturn:
    raise Exception(msg)


GLOBALS: dict[str, Callable[..., Any]] = {
    "now": now,
    "timedelta": datetime.timedelta,
    "raise": raise_helper,
}
