import logging

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import GameTaskResponseSchema
from db.models import GameTask

logger = logging.getLogger(__name__)


class GameTaskRepository:

    @staticmethod
    async def get_tasks_by_game_name(
        session: AsyncSession, game_name: str, limit: int = 10, offset: int = 0
    ) -> list[GameTaskResponseSchema]:
        try:
            stmt = (
                select(GameTask)
                .where(GameTask.game_name == game_name)
                .order_by(GameTask.id.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            game_tasks = result.scalars().all()
            return [GameTaskResponseSchema.model_validate(game_task) for game_task in game_tasks]
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching tasks for game_name={game_name}: {e}')
            return []

    @staticmethod
    async def count_tasks_by_game(session: AsyncSession, game_name: str) -> int:
        try:
            total_tasks = await session.execute(
                select(func.count()).select_from(GameTask).where(GameTask.game_name == game_name)
            )
            return total_tasks.scalar_one_or_none() or 0
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while counting tasks for game_name={game_name}: {e}')
            return 0
