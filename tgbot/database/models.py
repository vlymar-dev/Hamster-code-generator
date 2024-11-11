from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import ARRAY

from tgbot.database.base import Base


class User(Base):
    __tablename__ = 'users'

    # Basic user info
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )

    # Account settings
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    user_status: Mapped[str] = mapped_column(String(20), default='free')
    user_role: Mapped[str] = mapped_column(String(20), default='user')
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)

    # Referral info
    referred_by: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=True)
    referrals: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), default=[])

    # Activity
    total_keys_generated: Mapped[int] = mapped_column(Integer, default=0)
    daily_requests_count: Mapped[int] = mapped_column(Integer, default=0)
    last_request_datetime: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )