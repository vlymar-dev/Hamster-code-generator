from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.repositories.announcement_repo import AnnouncementRepository
from infrastructure.repositories.referral_repo import ReferralRepository
from infrastructure.repositories.user_repo import UserRepository


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            data['user_repo'] = UserRepository(session)
            data['announcement_repo'] = AnnouncementRepository(session)
            data['referral_repo'] = ReferralRepository(session)
            return await handler(event, data)
