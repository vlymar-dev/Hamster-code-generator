import logging

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import PromoCodeReceiveSchema
from db.models import PromoCode

logger = logging.getLogger(__name__)


class PromoCodeRepository:

    @staticmethod
    async def get_promo_codes(session: AsyncSession, game_names: list[str]) -> list[PromoCodeReceiveSchema]:
        try:
            result = await session.execute(
                select(PromoCode)
                .where(PromoCode.game_name.in_(game_names))
                .order_by(PromoCode.game_name, PromoCode.id)
            )
            promo_codes = result.scalars().all()
            return [PromoCodeReceiveSchema.model_validate(promo_code) for promo_code in promo_codes]
        except SQLAlchemyError as e:
            logger.error(f'Database error when retrieving promo codes: {e}')
            raise

    @staticmethod
    async def delete_promo_codes(session: AsyncSession, promo_code_ids: list[int]) -> None:
        try:
            await session.execute(
                delete(PromoCode)
                .where(PromoCode.id.in_(promo_code_ids))
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error when deleting promo codes: {e}')
            raise
