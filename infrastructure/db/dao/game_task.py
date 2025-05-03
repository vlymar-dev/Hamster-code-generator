import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao.base import BaseDAO
from infrastructure.db.models import GameTask

logger = logging.getLogger(__name__)


class GameTaskDAO(BaseDAO[GameTask]):
    """DAO for game task management."""

    model = GameTask

    @classmethod
    async def paginate_by_game_name(
        cls, session: AsyncSession, game_name: str, limit: int = 10, offset: int = 0
    ) -> list[GameTask]:
        """Get tasks by game name with pagination.

        Args:
            session: The database session.
            game_name: The name of the game to filter tasks by.
            limit: The maximum number of tasks to return (default 10).
            offset: The number of tasks to skip (default 0).

        Returns:
            A list of GameTask objects that match the game name.
        """
        logger.debug(f'Fetching tasks for game {game_name} with limit {limit} and offset {offset}')
        try:
            query = (
                select(cls.model)
                .where(cls.model.game_name == game_name)
                .order_by(cls.model.id.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(query)
            tasks = list(result.scalars().all())
            logger.info(f'Fetched {len(tasks)} tasks for game {game_name}')
            return tasks
        except SQLAlchemyError as e:
            logger.error(f'Failed to fetch tasks for game {game_name}: {e}', exc_info=True)
            raise
