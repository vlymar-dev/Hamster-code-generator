import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.common import ImageManager
from bot.handlers import ROUTERS
from bot.middlewares import CustomI18nMiddleware, DatabaseMiddleware
from bot.middlewares.image_manager_middleware import ImageManagerMiddleware
from core import BASE_DIR, config
from logging_config import setup_logging

setup_logging('tgbot')

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=config.telegram.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    image_manager = ImageManager(BASE_DIR)
    image_manager.load_category('handlers', 'handlers_images')

    dp.update.outer_middleware(ImageManagerMiddleware(image_manager))
    dp.update.outer_middleware(DatabaseMiddleware())
    CustomI18nMiddleware(
        path='bot/locales',
        default_locale=config.telegram.DEFAULT_LANGUAGE,
        domain='messages',
    ).setup(dp)

    for router in ROUTERS:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
