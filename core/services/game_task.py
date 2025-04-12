import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import GameTaskResponsePaginateSchema
from db.repositories import GameTaskRepository

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
        logger.debug(
            f'Getting paginated tasks for game \'{game_name}\' - '
            f'Page: {page}, Per page: {tasks_per_page}'
        )

        if page < 1:
            logger.warning(f'Invalid page number ({page}), resetting to 1')
            page = 1
        offset = (page - 1) * tasks_per_page

        try:
            total_tasks = await GameTaskRepository.count_tasks_by_game(session, game_name)
            tasks = await GameTaskRepository.get_tasks_by_game_name(
                session=session,
                game_name=game_name,
                limit=tasks_per_page,
                offset=offset
            )

            total_pages = max((total_tasks + tasks_per_page - 1) // tasks_per_page, 1)

            if page > total_pages:
                page = total_pages

            return GameTaskResponsePaginateSchema(
                tasks=tasks,
                page=page,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f'Error fetching paginated tasks: {e}', exc_info=True)
            raise
