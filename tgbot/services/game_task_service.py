import logging
from typing import Optional

from infrastructure.models.game_task import GameTask
from infrastructure.repositories.game_task_repo import GameTaskRepository

logger = logging.getLogger(__name__)

class GameTaskService:

    @staticmethod
    async def create_task(game_name: str, task: str, answer: str, task_repo: GameTaskRepository) -> GameTask:
        new_task = GameTask(game_name=game_name, task=task, answer=answer)
        try:
            await task_repo.add_task(new_task)
            logger.info(f"Task created successfully for game: {game_name}")
            return new_task
        except Exception as e:
            logger.error(f"Failed to create task for game_name={game_name}: {e}")
            raise

    @staticmethod
    async def get_task_by_id(task_id: int, task_repo: GameTaskRepository) -> Optional[GameTask]:
        task = await task_repo.get_task_by_id(task_id)
        if task:
            logger.info(f"Retrieved task with ID: {task_id}")
        else:
            logger.warning(f"Task with ID {task_id} not found.")
        return task

    @staticmethod
    async def get_tasks_by_game_name(
        game_name: str, task_repo: GameTaskRepository, limit: int = 20, offset: int = 0
    ) -> list[GameTask]:
        tasks = await task_repo.get_tasks_by_game_name(game_name, limit, offset)
        logger.info(f"Retrieved {len(tasks)} tasks for game_name={game_name} with limit={limit} and offset={offset}")
        return tasks

    @staticmethod
    async def update_task(task_id: int, game_name: str, task: Optional[str], answer: Optional[str], task_repo: GameTaskRepository) -> bool:
        try:
            updated = await task_repo.update_task(task_id, game_name, task, answer)
            if updated:
                logger.info(f"Task with ID {task_id} updated successfully.")
            else:
                logger.warning(f"Task with ID {task_id} not updated.")
            return updated
        except Exception as e:
            logger.error(f"Failed to update task with ID={task_id}: {e}")
            raise

    @staticmethod
    async def delete_task(task_id: int, game_name: str, task_repo: GameTaskRepository) -> bool:
        try:
            deleted = await task_repo.delete_task(task_id, game_name)
            if deleted:
                logger.info(f"Task with ID {task_id} deleted successfully.")
            else:
                logger.warning(f"Task with ID {task_id} not deleted.")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete task with ID={task_id}: {e}")
            raise

    @staticmethod
    async def count_tasks_by_game(game_name: str, task_repo: GameTaskRepository) -> int:
        try:
            count = await task_repo.count_tasks_by_game(game_name)
            logger.info(f"Game {game_name} has {count} tasks.")
            return count
        except Exception as e:
            logger.error(f"Failed to count tasks for game_name={game_name}: {e}")
            return 0

    @staticmethod
    async def get_random_task_for_game(game_name: str, task_repo: GameTaskRepository) -> Optional[GameTask]:
        try:
            tasks = await task_repo.get_tasks_by_game_name(game_name)
            if tasks:
                import random
                random_task = random.choice(tasks)
                logger.info(f"Random task retrieved for game {game_name}: {random_task.id}")
                return random_task
            logger.warning(f"No tasks available for game {game_name}.")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve random task for game_name={game_name}: {e}")
            return None

    @staticmethod
    async def verify_task_answer(task_id: int, user_answer: str, task_repo: GameTaskRepository) -> bool:
        try:
            task = await task_repo.get_task_by_id(task_id)
            if task:
                is_correct = task.answer.strip().lower() == user_answer.strip().lower()
                logger.info(f"Answer verification for task {task_id}: {'correct' if is_correct else 'incorrect'}")
                return is_correct
            logger.warning(f"Task with ID {task_id} not found for verification.")
            return False
        except Exception as e:
            logger.error(f"Failed to verify answer for task_id={task_id}: {e}")
            return False

    @staticmethod
    async def get_paginated_response(
        game_task_repo: GameTaskRepository,
        game_name: str,
        page: int,
        tasks_per_page: int = 20,
    ) -> tuple[list[GameTask], int, int]:
        """
        Gets the tasks for the specified game and page.
        Returns the tasks, the current page and the total number of pages.
        """
        offset = (page - 1) * tasks_per_page

        tasks = await game_task_repo.get_tasks_by_game_name(game_name, limit=tasks_per_page, offset=offset)

        total_tasks = await game_task_repo.count_tasks_by_game(game_name)
        total_pages = (total_tasks + tasks_per_page - 1) // tasks_per_page

        return tasks, page, total_pages