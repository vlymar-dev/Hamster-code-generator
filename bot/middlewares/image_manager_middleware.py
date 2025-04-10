from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.common import ImageManager


class ImageManagerMiddleware(BaseMiddleware):

    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager

    async def __call__(self, handler: Callable, event: TelegramObject, data: dict[str, Any]) -> Any:
        try:
            data['image_manager'] = self.image_manager
            return await handler(event, data)
        except Exception as e:
            print(f'ImageManager error: {e}')
            raise
