from datetime import datetime


def get_current_time() -> datetime:
    return datetime.now()

def format_seconds_to_minutes_and_seconds(seconds: int) -> str:
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if minutes > 0 :
        return f'{minutes} {remaining_seconds}'
    return f'{remaining_seconds}'
