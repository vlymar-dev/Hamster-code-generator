from datetime import date, datetime
from typing import Optional


def get_current_time() -> datetime:
    return datetime.now()


def get_current_date() -> date:
    return datetime.now().date()


def format_seconds_to_minutes_and_seconds(seconds: int) -> dict[str, Optional[int]]:
    minutes = seconds // 60
    seconds = seconds % 60
    return {'min': minutes if minutes > 0 else None, 'sec': seconds}
