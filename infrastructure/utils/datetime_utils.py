from datetime import date, datetime


def get_current_time() -> datetime:
    return datetime.now()


def get_current_date() -> date:
    return datetime.now().date()
