import logging
from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.repositories import UserRepository

logger = logging.getLogger(__name__)


class CustomI18nMiddleware(I18nMiddleware):
    """Provides localization using user preferences from database."""

    def __init__(self, path: str, default_locale: str, domain: str):
        """Initializes localization engine with provided settings."""
        self.i18n = I18n(path=path, default_locale=default_locale, domain=domain)
        super().__init__(self.i18n)

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """Determines user locale from database or uses default."""
        if not event.from_user:
            logger.warning(
                f'Localization failed - no user in event. Event type: {type(event).__name__}'
            )
            return self.i18n.default_locale

        session: AsyncSession = data.get('session')
        if not session:
            logger.error(
                f'Localization failed for user {event.from_user.id} - no database session'
            )
            return self.i18n.default_locale

        user_id = event.from_user.id
        logger.debug(f'Starting locale detection for user {user_id}')

        try:
            locale = await self._fetch_user_language(session, user_id)
            if locale:
                logger.debug(f'Found locale "{locale}" for user {user_id}')
            else:
                logger.debug(f'Using default locale for user {user_id}')
            return locale or self.i18n.default_locale
        except Exception as e:
            logger.error(
                f'Locale detection failed for user {user_id}. Error: {str(e)}'
            )
            return self.i18n.default_locale

    async def _fetch_user_language(self, session: AsyncSession, user_id: int) -> str:
        """Fetches user's language preference from the database."""
        logger.debug(f'Querying language for user {user_id}')
        try:
            result = await UserRepository.get_user_language(session, user_id)
            logger.debug(f'Language query result for user {user_id}: {result}')
            return result or self.i18n.default_locale
        except Exception as e:
            logger.error(
                f'Database error during language query for user {user_id}. Error: {str(e)}'
            )
            return self.i18n.default_locale
