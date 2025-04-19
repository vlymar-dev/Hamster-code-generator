import logging
from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.services import CacheService, UserCacheService

logger = logging.getLogger(__name__)


class CustomI18nMiddleware(I18nMiddleware):
    """Middleware for providing localization based on user preferences.

    Uses cache service as primary source for language preferences with fallback
    to database if needed. If no user language is found, uses default locale.
    """

    def __init__(self, path: str, default_locale: str, domain: str):
        """Initializes localization engine with provided settings."""
        self.i18n = I18n(path=path, default_locale=default_locale, domain=domain)
        super().__init__(self.i18n)

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """Determine user locale from cache/database or use default."""
        if not event.from_user:
            logger.warning(f'Localization failed - no user in event. Event type: {type(event).__name__}')
            return self.i18n.default_locale

        session: AsyncSession = data.get('session')
        cache_service: CacheService = data.get('cache_service')
        if not session or not cache_service:
            logger.error(
                f'Localization failed for user {event.from_user.id} - '
                f'missing required services (session: {bool(session)}, cache: {bool(cache_service)})'
            )
            return self.i18n.default_locale

        user_id = event.from_user.id
        logger.debug(f'Starting locale detection for user {user_id}')

        try:
            language_data = await UserCacheService.get_user_language(cache_service, session, user_id)
            locale = language_data.language_code
            if locale:
                logger.debug(f'Resolved locale "{locale}" for user {user_id}')
                return locale
            else:
                logger.debug(f'Using default locale for user {user_id}')
                return self.i18n.default_locale
        except Exception as e:
            logger.error(f'Locale detection failed for user {user_id}. Error: {str(e)}')
            return self.i18n.default_locale
