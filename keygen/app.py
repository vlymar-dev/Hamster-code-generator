import asyncio
import logging

from infrastructure import setup_logging
from keygen.game_promo_manager import gen
from keygen.games import games

setup_logging(app_name='app')

logger = logging.getLogger(__name__)


async def run_all_games():
    tasks = [gen(game) for game in games]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        logger.info('✅ | Starting `app` application')
        asyncio.run(run_all_games())
    except KeyboardInterrupt:
        logger.info('🛑 | App application is terminated by the `Ctrl+C` signal')
