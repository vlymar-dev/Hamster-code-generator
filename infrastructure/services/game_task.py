import logging

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao import GameTaskDAO
from infrastructure.db.models import GameTask
from infrastructure.schemas import GameTaskResponsePaginateSchema, GameTaskSchema

logger = logging.getLogger(__name__)


class GameTaskService:
    """Service for handling game task pagination operations"""

    @staticmethod
    async def get_paginated_response(
        session: AsyncSession,
        game_name: str,
        page: int = 1,
        tasks_per_page: int = 10,
    ):
        """Get paginated list of game tasks with metadata"""
        logger.debug(f"Getting paginated tasks for game '{game_name}' - Page: {page}, Per page: {tasks_per_page}")

        if page < 1:
            logger.warning(f'Invalid page number ({page}), resetting to 1')
            page = 1
        offset = (page - 1) * tasks_per_page

        try:
            total_tasks = await GameTaskDAO.count_where(session, GameTask.game_name == game_name)
            list_tasks = await GameTaskDAO.paginate_by_game_name(
                session=session, game_name=game_name, limit=tasks_per_page, offset=offset
            )
            tasks = [GameTaskSchema.model_validate(game_task) for game_task in list_tasks]

            total_pages = max((total_tasks + tasks_per_page - 1) // tasks_per_page, 1)

            if page > total_pages:
                page = total_pages

            return GameTaskResponsePaginateSchema(tasks=tasks, page=page, total_pages=total_pages)
        except Exception as e:
            logger.error(f'Error fetching paginated tasks: {e}', exc_info=True)
            raise
