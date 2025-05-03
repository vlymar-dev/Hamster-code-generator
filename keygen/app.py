import asyncio
import logging

from keygen.game_promo_manager import gen
from keygen.games import games

logger = logging.getLogger(__name__)


async def run_all_games():
    tasks = [gen(game) for game in games]
    await asyncio.gather(*tasks)


async def start_keygen():
    try:
        logger.info('Starting Keygen')
        await run_all_games()
    except Exception as e:
        logger.error(f'Error during keygen startup: {e}')
        raise
