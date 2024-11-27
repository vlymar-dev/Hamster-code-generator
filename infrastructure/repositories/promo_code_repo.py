import logging

from sqlalchemy import delete, func, select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.promo_code import PromoCode

logger = logging.getLogger(__name__)


class PromoCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_promo_code(self, game_name: str, promo_code: str) -> PromoCode:
        try:
            new_code = PromoCode(game_name=game_name, promo_code=promo_code)
            self.session.add(new_code)
            await self.session.commit()
            await self.session.refresh(new_code)
            return new_code
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error when adding a promo code: {e}')
            raise

    async def get_code_count_for_game(self, game_name: str) -> int:
        try:
            result = await self.session.scalar(
                select(func.count(PromoCode.id))
                .where(PromoCode.game_name == game_name)
            )
            return result or 0
        except DatabaseError as e:
            logger.error(f'Database error when receiving the number of codes by games: {e}')
            raise

    async def get_promo_codes(self, game_names: list[str]) -> list[PromoCode]:
        try:
            result = await self.session.execute(
                select(PromoCode)
                .where(PromoCode.game_name.in_(game_names))
                .order_by(PromoCode.game_name, PromoCode.id)
            )
            return list(result.scalars().all())
        except DatabaseError as e:
            logger.error(f'Database error when retrieving promo codes: {e}')
            raise

    async def delete_promo_codes(self, promo_code_ids: list[int]) -> None:
        try:
            await self.session.execute(
                delete(PromoCode)
                .where(PromoCode.id.in_(promo_code_ids))
            )
            await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error when deleting promo codes: {e}')
            raise
