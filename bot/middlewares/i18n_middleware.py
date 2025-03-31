from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import UserRepository


class CustomI18nMiddleware(I18nMiddleware):

    def __init__(self, domain: str, path: str):
        self.i18n = I18n(path=path, default_locale='en', domain=domain)
        super().__init__(self.i18n)

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        session: AsyncSession = data.get('session')

        if not event.from_user or not session:
            return self.i18n.default_locale

        return await self._fetch_user_language(session, event.from_user.id)

    async def _fetch_user_language(self, session: AsyncSession, user_id: int) -> str:
        """Fetches the user's language from the database."""
        return await UserRepository.get_user_language(session,user_id) or self.i18n.default_locale
