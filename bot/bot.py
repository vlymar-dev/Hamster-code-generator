import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import register_handlers
from bot.middlewares.database_middleware import DatabaseMiddleware

# from bot.middlewares.db_middleware import DatabaseMiddleware
from bot.middlewares.i18n_middleware import CustomI18nMiddleware

# from bot.config import config
from core import config

# from infrastructure.database import async_session_maker
from logging_config import setup_logging

setup_logging('tgbot')

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=config.telegram.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(DatabaseMiddleware())
    # dp.update.outer_middleware(DatabaseMiddleware(session_maker=async_session_maker))
    # dp.update.outer_middleware(CustomI18nMiddleware(domain='messages', path='bot/locales'))
    CustomI18nMiddleware(domain='messages', path='bot/locales').setup(dp)

    register_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
