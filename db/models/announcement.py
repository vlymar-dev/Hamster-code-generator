from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class Announcement(Base):
    __tablename__ = 'announcements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0)
    )
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    translations_text = relationship(
        'AnnouncementTranslation',
        back_populates='announcement',
        cascade='all, delete-orphan'
    )


class AnnouncementTranslation(Base):
    __tablename__ = 'announcement_translations'
    __table_args__ = (
        UniqueConstraint('announcement_id', 'language_code', name='uc_announcement_language'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    announcement_id: Mapped[int] = mapped_column(Integer, ForeignKey('announcements.id'), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    text: Mapped[str] = mapped_column(String(3500), nullable=False)

    announcement = relationship('Announcement', back_populates='translations_text')
