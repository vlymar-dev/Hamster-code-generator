import logging
from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from infrastructure.services import CacheService

logger = logging.getLogger(__name__)


class CacheServiceMiddleware(BaseMiddleware):
    """Middleware that provides CacheService to handlers."""

    def __init__(self, cache_service: CacheService):
        """Initialize with cache service instance."""
        self.cache_service = cache_service
        logger.debug('CacheServiceMiddleware initialized')

    async def __call__(self, handler: Callable, event: TelegramObject, data: dict[str, Any]) -> Any:
        """Inject cache service into handler context."""
        try:
            logger.debug('Injecting cache service into handler')
            data['cache_service'] = self.cache_service
            return await handler(event, data)
        except Exception as e:
            logger.error(f'CacheServiceMiddleware error: {e}', exc_info=True)
            raise
