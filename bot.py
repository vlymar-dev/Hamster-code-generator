import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from tgbot.config import config
from tgbot.handlers import register_handlers
from tgbot.middlewares.db import DatabaseMiddleware
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware


logger = logging.getLogger(__name__)



async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    engine = create_async_engine(url=config.db.db_url, echo=False, pool_size=3, max_overflow=5)
    session = async_sessionmaker(bind=engine, expire_on_commit=False)

    dp.update.outer_middleware(DatabaseMiddleware(session=session))
    dp.update.outer_middleware(CustomI18nMiddleware(domain='messages', path='tgbot/locales'))

    register_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
