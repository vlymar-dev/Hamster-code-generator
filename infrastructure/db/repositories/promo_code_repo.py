import logging

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models import PromoCode
from infrastructure.schemas import PromoCodeReceiveSchema
from infrastructure.schemas.promo_code import PromoCodeCreateSchema

logger = logging.getLogger(__name__)


class PromoCodeRepository:
    @staticmethod
    async def add_promo_code(session: AsyncSession, data: PromoCodeCreateSchema) -> PromoCode:
        try:
            code = PromoCode(**data.model_dump())
            session.add(code)
            await session.commit()
            await session.refresh(code)
            return code
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error when adding a promo code: {e}')

    @staticmethod
    async def get_promo_codes(session: AsyncSession, game_names: list[str]) -> list[PromoCodeReceiveSchema]:
        try:
            result = await session.execute(
                select(PromoCode).where(PromoCode.game_name.in_(game_names)).order_by(PromoCode.game_name, PromoCode.id)
            )
            promo_codes = result.scalars().all()
            return [PromoCodeReceiveSchema.model_validate(promo_code) for promo_code in promo_codes]
        except SQLAlchemyError as e:
            logger.error(f'Database error when retrieving promo codes: {e}')
            raise

    @staticmethod
    async def delete_promo_codes(session: AsyncSession, promo_code_ids: list[int]) -> None:
        try:
            await session.execute(delete(PromoCode).where(PromoCode.id.in_(promo_code_ids)))
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error when deleting promo codes: {e}')
            raise

    @staticmethod
    async def get_code_counts_for_games(session: AsyncSession, game_names: list[str]) -> dict[str, int]:
        try:
            result = await session.execute(
                select(PromoCode.game_name, func.count(PromoCode.id).label('count'))
                .where(PromoCode.game_name.in_(game_names))
                .group_by(PromoCode.game_name)
            )
            counts = {row.game_name: row.count for row in result.fetchall()}
            for game_name in game_names:
                if game_name not in counts:
                    counts[game_name] = 0
            return counts
        except SQLAlchemyError as e:
            logger.error(f'Database error when retrieving code counts for games: {e}')
            raise
