from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import GameTaskResponsePaginateSchema
from db.repositories import GameTaskRepository


class GameTaskService:

    @staticmethod
    async def get_paginated_response(
            session: AsyncSession,
            game_name: str,
            page: int = 1,
            tasks_per_page: int = 10,
    ):
        if page < 1:
            page = 1
        offset = (page - 1) * tasks_per_page

        total_tasks = await GameTaskRepository.count_tasks_by_game(session, game_name)
        tasks =  await GameTaskRepository.get_tasks_by_game_name(
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
