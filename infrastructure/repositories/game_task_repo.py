import logging
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.game_task import GameTask

logger = logging.getLogger(__name__)


class GameTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_task(self, game_task: GameTask) -> None:
        try:
            result = await self.session.execute(
                select(GameTask).where(GameTask.id == game_task.id)
            )
            existing_task = result.scalar_one_or_none()
            if not existing_task:
                self.session.add(game_task)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f'Integrity error occurred while adding task: {e}')
            raise
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while adding task: {e}')
            raise

    async def get_task_by_id(self, task_id: int) -> Optional[GameTask]:
        try:
            task = await self.session.get(GameTask, task_id)
            return task
        except DatabaseError as e:
            logger.error(f'Database error occurred while fetching task by id {task_id}: {e}')
            return None

    async def get_tasks_by_game_name(
        self, game_name: str, limit: int = 20, offset: int = 0
    ) -> list[GameTask]:
        try:
            stmt = (
                select(GameTask)
                .where(GameTask.game_name == game_name)
                .order_by(GameTask.id.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = list(result.scalars().all())
            return tasks
        except DatabaseError as e:
            logger.error(f'Database error occurred while fetching tasks for game_name={game_name}: {e}')
            return []

    async def delete_task(self, task_id: int, game_name: str) -> bool:
        try:
            stmt = delete(GameTask).where(
                GameTask.id == task_id, GameTask.game_name == game_name
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while deleting task_id={task_id}: {e}')
            return False

    async def count_tasks_by_game(self, game_name: str) -> int:
        try:
            result = await self.session.execute(
                select(func.count()).where(GameTask.game_name == game_name)
            )
            return result.scalar_one_or_none() or 0
        except DatabaseError as e:
            logger.error(f'Database error occurred while counting tasks for game_name={game_name}: {e}')
            return 0