import logging
from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao.base import BaseDAO
from infrastructure.db.models import User

logger = logging.getLogger(__name__)


class UserDAO(BaseDAO[User]):
    """DAO for user management."""

    model = User

    @classmethod
    async def check_user_exists(cls, session: AsyncSession, user_id: int) -> bool:
        """Checks if a user with the given ID exists."""
        try:
            return await session.get(cls.model, user_id) is not None
        except SQLAlchemyError as e:
            logger.error(f'Error occurred while checking user exists: {e}')
            raise

    @classmethod
    async def find_today_keys_count(cls, session: AsyncSession) -> int:
        """Counts today's keys"""
        try:
            today = date.today()
            result = await session.execute(
                select(func.sum(cls.model.daily_requests_count)).where(
                    cast(cls.model.last_request_datetime, Date) == today
                )
            )
            count = result.scalar_one_or_none()
            return count if count else 0
        except SQLAlchemyError as e:
            logger.error(f'Error counting today keys: {e}')
            return 0

    @classmethod
    async def find_all_where(cls, session: AsyncSession, *where_conditions) -> list[User]:
        """Finds all records matching WHERE conditions.

        Args:
            session (AsyncSession): The database session.
            where_conditions: Arbitrary SQLAlchemy where conditions.

        Returns:
            list[User]: The list of matching records.
        """
        logger.info(f'Finding all {cls.model.__name__} records with custom WHERE conditions.')
        try:
            query = select(cls.model).where(*where_conditions)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f'Found {len(records)} records.')
            return list(records)
        except SQLAlchemyError as e:
            logger.error(f'Error fetching records with WHERE clause: {e}')
            raise
