from datetime import datetime
from zoneinfo import ZoneInfo

from sigma_core.shared_kernel.value_objects import Timestamp


MADRID_TZ = ZoneInfo("Europe/Madrid")


def ts(
    year: int = 2026,
    month: int = 4,
    day: int = 10,
    hour: int = 12,
    minute: int = 0,
) -> Timestamp:
    """Build a Madrid-tz Timestamp. Handy for tests involving timer clocks."""
    return Timestamp(datetime(year, month, day, hour, minute, tzinfo=MADRID_TZ))
