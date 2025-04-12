import logging

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models import GameTask
from infrastructure.schemas import GameTaskSchema

logger = logging.getLogger(__name__)


class GameTaskRepository:

    @staticmethod
    async def add_task(session: AsyncSession, game_task: GameTaskSchema) -> None:
        try:
            task = GameTask(**game_task.model_dump())
            session.add(task)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding task: {e}')

    @staticmethod
    async def get_tasks_by_game_name(
        session: AsyncSession, game_name: str, limit: int = 10, offset: int = 0
    ) -> list[GameTaskSchema]:
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
            return [GameTaskSchema.model_validate(game_task) for game_task in game_tasks]
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching tasks for game_name={game_name}: {e}')
            return []

    @staticmethod
    async def get_task_by_id(self, task_id: int) -> GameTaskSchema | None:
        try:
            game_task = await self.session.get(GameTask, task_id)
            return GameTaskSchema.model_validate(game_task)
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching task by id {task_id}: {e}')
            return None

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

    @staticmethod
    async def delete_task_by_id(session: AsyncSession, task_id: int) -> None:
        try:
            await session.execute(delete(GameTask).where(GameTask.id == task_id))
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while deleting task_id={task_id}: {e}')
