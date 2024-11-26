import logging
from typing import Optional

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

    async def pop_code_by_game(self, game_name: str) -> Optional[str]:
        """
        Get and remove one promo code for the specified game.
        """
        try:
            async with self.session.begin():
                result = await self.session.execute(
                    select(PromoCode)
                    .where(PromoCode.game_name == game_name)
                    .order_by(PromoCode.id)
                    .limit(1)
                )
                code_to_delete = result.scalar()
                if not code_to_delete:
                    return None
                promo_code = code_to_delete.promo_code
                await self.session.execute(
                    delete(PromoCode).where(PromoCode.id == code_to_delete.id)
                )
                return promo_code
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error when deleting codes: {e}')
            raise

