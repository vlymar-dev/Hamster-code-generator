from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class PromoCode(Base):
    __tablename__ = 'promo_codes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_name: Mapped[str] = mapped_column(String(50), nullable=False)
    promo_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    __table_args__ = (Index('ix_game_name_id', 'game_name', 'id'),)
