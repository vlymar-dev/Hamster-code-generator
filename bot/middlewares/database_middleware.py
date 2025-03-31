from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from db.database import async_session_maker


class DatabaseMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        """

        Args:
            handler (Callable): The next middleware or handler function.
            event (Message | CallbackQuery): The incoming Telegram event.
            data (dict[str, Any]): Context data passed through middlewares.

        Returns:
            Any: The result of the handler execution.
        """
        async with async_session_maker() as session:
            data['session'] = session
            return await handler(event, data)
