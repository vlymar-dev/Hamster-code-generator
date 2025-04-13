import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.common import ImageManager
from bot.handlers import ROUTERS
from bot.middlewares import CacheServiceMiddleware, CustomI18nMiddleware, DatabaseMiddleware, ImageManagerMiddleware
from infrastructure import BASE_DIR, config, setup_logging
from infrastructure.services import CacheService

setup_logging(app_name='bot')

logger = logging.getLogger(__name__)


async def main():
    bot = None
    redis_client = None

    try:
        logger.info('Starting bot initialization...')

        # Cache Redis initialization
        redis_client = Redis.from_url(
            config.redis.dsn,
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info('✅ Redis connection established')

        bot = Bot(
            token=config.telegram.TOKEN.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        storage = RedisStorage(
            redis=redis_client,
            state_ttl=config.redis.FSM_TTL or 3600,
            data_ttl=config.redis.DATA_TTL or 7200
        )
        logger.debug(f'Using storage: {type(storage).__name__}')
        dp = Dispatcher(storage=storage)

        # ImageManager initialization
        image_manager = ImageManager(BASE_DIR)
        logger.debug(f'Initializing ImageManager with base directory: {BASE_DIR}')
        image_manager.load_category('handlers', 'handlers_images')
        logger.info('Loaded {} images for category \'handlers\''.format(
            len(image_manager.categories.get('handlers', []))
        ))

        # CacheService initialization
        cache_service = CacheService(
            redis=redis_client,
            default_ttl=config.redis.TTL
        )

        # Middleware setup
        logger.debug('Setting up middlewares...')
        dp.update.outer_middleware(CacheServiceMiddleware(cache_service))
        dp.update.outer_middleware(ImageManagerMiddleware(image_manager))
        dp.update.outer_middleware(DatabaseMiddleware())
        CustomI18nMiddleware(
            path='bot/locales',
            default_locale=config.telegram.DEFAULT_LANGUAGE,
            domain='messages',
        ).setup(dp)
        logger.info('Middlewares configured successfully')

        # Routers
        logger.debug('Including routers...')
        for i, router in enumerate(ROUTERS, 1):
            dp.include_router(router)
            logger.debug(f'({i}/{len(ROUTERS)}) Included router: {router.name}')
        logger.info(f'Total {len(ROUTERS)} routers registered')

        # Start polling
        logger.info('Starting bot polling...')
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f'Critical error during bot initialization: {str(e)}', exc_info=True)
        raise
    finally:
        logger.info('🛑 Bot shutdown completed')
        if redis_client:
            await redis_client.close()
        if bot:
            await bot.session.close()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
