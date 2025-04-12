import logging
from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.common import ImageManager

logger = logging.getLogger(__name__)


class ImageManagerMiddleware(BaseMiddleware):
    """Injects ImageManager instance into handler context for image processing."""

    def __init__(self, image_manager: ImageManager):
        """Initializes middleware with provided ImageManager instance."""
        self.image_manager = image_manager

    async def __call__(self, handler: Callable, event: TelegramObject, data: dict[str, Any]) -> Any:
        """Handles image manager injection and error logging for event processing."""
        event_type = event.event_type if hasattr(event, 'event_type') else 'unknown_event'
        logger.debug(f'Processing {event_type} with ImageManager')

        try:
            data['image_manager'] = self.image_manager
            logger.debug(f'Successfully injected ImageManager for {event_type}.')
            result = await handler(event, data)
            logger.debug(f'ImageManager processing completed for {event_type}')
            return result
        except Exception as e:
            logger.error(
                f'ImageManager failure in {event_type}. '
                f'Error: {str(e)}. '
            )
            logger.debug(f'Error details - Event data: {event.model_dump_json()}')
            raise
