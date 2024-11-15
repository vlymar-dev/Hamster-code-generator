from sqlalchemy import Column, DateTime, Integer, String

from infrastructure.models.base import Base


class Announcement(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime, nullable=False)
    created_by = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Announcement(title='{self.title}', created_by='{self.created_by}')>"
