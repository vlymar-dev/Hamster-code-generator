from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserLanguageCodeSchema(BaseModel):
    language_code: str


class UserSubscriptionSchema(BaseModel):
    is_subscribed: bool


class UserRoleSchema(BaseModel):
    user_role: str


class UserAuthSchema(UserRoleSchema):
    is_banned: bool


class UserDailyRequestsSchema(UserRoleSchema):
    daily_requests_count: int


class UserCreateSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str


class SubscribedUsersSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    language_code: str


class UserProgressSchema(BaseModel):
    registration_date: datetime
    user_status: str
    total_keys_generated: int


class UserProgressDataSchema(BaseModel):
    total_keys: int
    user_status: str
    days_in_bot: int
    referrals: int
    current_level: str
    next_level: str | None
    keys_progress: str
    referrals_progress: str
    days_progress: str


class UpdateUserKeysSchema(BaseModel):
    total_keys_generated: int
    daily_requests_count: int
    last_request_datetime: datetime | None


class UserActivitySchema(UpdateUserKeysSchema):
    user_status: str


class RemainingTimeSchema(BaseModel):
    minutes: int = 0
    seconds: int = 0


class UserKeyGenerationSchema(BaseModel):
    can_generate: bool = False
    daily_limit_exceeded: bool = False
    remaining_time: RemainingTimeSchema | None = None
