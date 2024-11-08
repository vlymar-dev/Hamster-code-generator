from tgbot.database.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean, String


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    user_status: Mapped[str] = mapped_column(String(20), default='free')
