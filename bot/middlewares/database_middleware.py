import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from infrastructure.db.accessor import async_session_maker

logger = logging.getLogger(__name__)


class BaseDatabaseMiddleware(BaseMiddleware):
    """Base middleware for handling database sessions."""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        """Handles session lifecycle for the request.

        Args:
            handler (Callable): The next middleware or handler function.
            event (Message | CallbackQuery): The incoming Telegram event.
            data (dict[str, Any]): Context data passed through middlewares.

        Returns:
            Any: The result of the handler execution.
        """
        async with async_session_maker() as session:
            self.set_session(data, session)
            try:
                logger.debug(f'Database session {id(session)} opened')
                result = await handler(event, data)
                await self.after_handler(session)
                logger.debug(f'Database session {id(session)} closed successfully')
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f'Database error in session {id(session)}: {str(e)}')
                raise e

    def set_session(self, data: dict[str, Any], session) -> None:
        """Sets the session in the data dictionary.

        Args:
            data (dict[str, Any]): Context data.
            session (AsyncSession): The database session.
        """
        raise NotImplementedError('This method must be implemented in subclasses.')

    async def after_handler(self, session) -> None:
        """Executes actions after the handler, such as committing transactions.

        Args:
            session (AsyncSession): The database session.
        """
        pass


class DatabaseMiddlewareWithoutCommit(BaseDatabaseMiddleware):
    """Middleware that provides a database session without committing changes."""

    def set_session(self, data: dict[str, Any], session) -> None:
        data['session_without_commit'] = session


class DatabaseMiddlewareWithCommit(BaseDatabaseMiddleware):
    """Middleware that provides a database session and commits changes."""

    def set_session(self, data: dict[str, Any], session) -> None:
        data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
        await session.commit()
