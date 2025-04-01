from datetime import datetime

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str


class UserProgresSchema(BaseModel):
    registration_date: datetime
    user_status: str
    total_keys_generated: int

class UserProgressData(BaseModel):
    total_keys: int
    user_status: str
    days_in_bot: int
    referrals: int
    current_level: str
    next_level: str | None
    keys_progress: str
    referrals_progress: str
    days_progress: str
