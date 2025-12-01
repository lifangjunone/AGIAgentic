
""" Time Tool for providing current time information、 formatted time strings、timezone conversions、 and time calculations.
"""

import pytz

from typing import Any, Dict
from langchain.tools import tool # type: ignore
from datetime import datetime, timedelta


@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """Get the current time in the specified timezone.

    Args:
        timezone (str): The timezone to get the current time for. Defaults to "Asia/Shanghai".

    Returns:
        str: The current time as a formatted string.
    """

    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S")

@tool
def get_time_info() -> Dict[str, Any]:
    """Get detailed information about the current time.

    Returns:
        Dict[str, Any]: A dictionary containing various time details.
    """
    cn_weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now = datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "weekday": now.strftime("%A"),
        "iso_format": now.isoformat(),
        "timestamp": int(now.timestamp()),
        "weekday_cn": cn_weekdays[now.weekday()],
    }

@tool
def calculate_date_offset(days: int = 0, hours: int = 0, minutes: int = 0) -> str:
    """Calculate the date and time after applying the specified offsets.

    Args:
        days (int): Number of days to offset. Defaults to 0.
        hours (int): Number of hours to offset. Defaults to 0.
        minutes (int): Number of minutes to offset. Defaults to 0.

    Returns:
        str: The calculated date and time as a formatted string.
    """
    now = datetime.now()
    offset = timedelta(days=days, hours=hours, minutes=minutes)
    new_time = now + offset
    return new_time.strftime("%Y-%m-%d %H:%M:%S")


# Define the public API of the module
__all__ = [
    "get_current_time",
    "get_time_info",
    "calculate_date_offset",
]

