from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.models.base import Base


class Announcement(Base):
    __tablename__ = 'announcements'

    id = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
