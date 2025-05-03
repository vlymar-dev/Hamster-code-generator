import logging

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao.base import BaseDAO
from infrastructure.db.models import PromoCode
from infrastructure.schemas import PromoCodeReceiveSchema

logger = logging.getLogger(__name__)


class PromoCodeDAO(BaseDAO[PromoCode]):
    """DAO for promo code management."""

    model = PromoCode

    @classmethod
    async def find_by_game_names(cls, session: AsyncSession, game_names: list[str]) -> list[PromoCodeReceiveSchema]:
        """Retrieves promo codes filtered by game names with ordering.

        Args:
            session: Database session
            game_names: List of game names to filter by

        Returns:
            List of PromoCodeReceiveSchema
        """
        logger.info(f'Fetching promo codes for games: {game_names}')
        try:
            result = await session.execute(
                select(cls.model).where(cls.model.game_name.in_(game_names)).order_by(cls.model.game_name, cls.model.id)
            )
            promo_codes = result.scalars().all()
            logger.info(f'Found {len(promo_codes)} promo codes')
            return [PromoCodeReceiveSchema.model_validate(pc) for pc in promo_codes]
        except SQLAlchemyError as e:
            logger.error(f'Database error when retrieving promo codes: {e}')
            raise

    @classmethod
    async def delete_by_ids(cls, session: AsyncSession, ids: list[int]) -> None:
        """Deletes records by list of IDs."""
        logger.info(f'Deleting {cls.model.__name__} with IDs: {ids}')
        try:
            await session.execute(delete(cls.model).where(cls.model.id.in_(ids)))
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Error deleting records by IDs: {e}')
            raise

    @classmethod
    async def find_code_counts_by_game_names(cls, session: AsyncSession, game_names: list[str]) -> dict[str, int]:
        """Replicates get_code_counts_for_games functionality in DAO style"""
        logger.info(f'Counting promo codes for games: {game_names}')
        try:
            result = await session.execute(
                select(cls.model.game_name, func.count(cls.model.id).label('count'))
                .where(cls.model.game_name.in_(game_names))
                .group_by(cls.model.game_name)
            )

            counts = {row.game_name: row.count for row in result}
            for game_name in game_names:
                counts.setdefault(game_name, 0)

            logger.info(f'Found code counts: {counts}')
            return counts

        except SQLAlchemyError as e:
            logger.error(f'Database error when counting promo codes: {e}')
            raise
