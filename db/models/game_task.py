from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class GameTask(Base):
    __tablename__ = 'game_tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
