import asyncio
import enum
import logging

from bot.bot import start_bot
from infrastructure import config, setup_logging
from keygen.app import start_keygen

setup_logging(app_name='hamster')
logger = logging.getLogger(__name__)


class StartupMethods(enum.Enum):
    KeygenAndBot = 0
    OnlyKeygen = 1
    OnlyBot = 2


async def main():
    try:
        method = StartupMethods(config.STARTUP_METHOD)
    except ValueError:
        logger.warning('Invalid STARTUP_METHOD, defaulting to OnlyBot')
        method = StartupMethods.OnlyBot

    tasks = []

    if method in (StartupMethods.OnlyKeygen, StartupMethods.KeygenAndBot):
        tasks.append(asyncio.create_task(start_keygen()))

    if method in (StartupMethods.OnlyBot, StartupMethods.KeygenAndBot):
        tasks.append(asyncio.create_task(start_bot()))

    if not tasks:
        logger.warning('No valid startup method selected. Exiting')
        return

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f'Task {i} failed: {result}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Gracefully shutting down on Ctrl+C')
