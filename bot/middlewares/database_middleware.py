import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from infrastructure.db.accessor import async_session_maker

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Provides database session management for request handlers."""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        """Manages database session lifecycle for the request."""
        async with async_session_maker() as session:
            data['session'] = session
            try:
                logger.debug(f'Database session {id(session)} opened')
                result = await handler(event, data)
                logger.debug(f'Database session {id(session)} closed successfully')
                return result
            except Exception as e:
                logger.error(f'Database error in session {id(session)}: {str(e)}')
                raise
            finally:
                logger.debug(f'Finalizing database session {id(session)}')
