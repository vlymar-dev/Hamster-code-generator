from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.models.base import Base


class Referral(Base):
    __tablename__ = 'referrals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    referred_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )
    referrer: Mapped['User'] = relationship(
        'User',
        back_populates='referrals',
        foreign_keys=[referrer_id]
    )