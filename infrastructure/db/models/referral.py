from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class Referral(Base):
    __tablename__ = 'referrals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), index=True)
    referred_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )
