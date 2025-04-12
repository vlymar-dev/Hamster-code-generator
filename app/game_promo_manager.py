# NOTE:
# =============================================================================
# 📌 CONTRIBUTION INVITE
# -----------------------------------------------------------------------------
# This code generator is currently a low priority for me, and I'm not actively
# maintaining or improving it.
#
# If you're interested in contributing, feel free to improve, refactor, or
# enhance this part of the project. Pull requests are very welcome!
#
# 💡 Suggestions:
# - Improve code structure
# - Add missing features or test coverage
# - Optimize performance or readability
#
# Thanks for your interest and support! ❤️
# =============================================================================

import asyncio
import json
import logging
import random
import time
import uuid
from urllib.parse import urlparse

import aiohttp

from infrastructure.db.accessor import async_session_maker
from infrastructure.db.repositories.promo_code_repo import PromoCodeRepository
from infrastructure.schemas.promo_code import PromoCodeCreateSchema

logger = logging.getLogger(__name__)


class GamePromo:
    def __init__(self, game):
        self.game = game
        self.token = None
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        await self.session.close()

    @staticmethod
    async def generate_client_id():
        timestamp = int(time.time() * 1000)
        random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(19))
        return f'{timestamp}-{random_numbers}'

    async def login_client(self):
        client_id = await self.generate_client_id()
        proxy = self.game['proxy']

        parsed_url = urlparse(f'http://{proxy}')
        username = parsed_url.username
        password = parsed_url.password
        ip = parsed_url.hostname
        port = parsed_url.port

        try:
            auth = aiohttp.BasicAuth(username, password) if username and password else None
            async with self.session.post(
                    'https://api.gamepromo.io/promo/login-client',
                    json={
                        'appToken': self.game['app_token'],
                        'clientId': client_id,
                        'clientOrigin': 'deviceid'
                    },
                    proxy=f'http://{proxy}',
                    proxy_auth=auth,
                    headers={
                        'Content-Type': 'application/json; charset=utf-8',
                    }
            ) as response:
                data = await response.json()
                self.token = data['clientToken']
                logger.info(
                    f'`{response.status}` ✅ | Token for game: `{self.game['name']}` | Proxy: `{ip}:{port}` generated'
                )
        except Exception as error:
            logger.error(
                f'`{response.status}` ⚠️ | Client login error `{self.game['name']}` | Proxy: `{ip}:{port}`| {error}'
            )
            await asyncio.sleep(random.uniform(0.1, 3) + 6)
            await self.login_client()

    async def register_event(self):
        event_id = str(uuid.uuid4())
        proxy = self.game['proxy']
        parsed_url = urlparse(f'http://{proxy}')
        ip = parsed_url.hostname
        port = parsed_url.port

        for attempt in range(self.game['attempts']):
            try:
                username = parsed_url.username
                password = parsed_url.password

                auth = aiohttp.BasicAuth(username, password) if username and password else None
                async with self.session.post(
                        'https://api.gamepromo.io/promo/register-event',
                        json={
                            'promoId': self.game['promo_id'],
                            'eventId': event_id,
                            'eventOrigin': 'undefined'
                        },
                        proxy=f'http://{proxy}',
                        proxy_auth=auth,
                        headers={
                            'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json; charset=utf-8',
                        }
                ) as response:
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        error_text = await response.text()
                        logger.error(
                            f'`{response.status}` ⚠️ | Game: `{self.game['name']}` | Proxy: ({ip}:{port}) | '
                            f'HTML Response: {error_text[:500]}...')
                        continue

                    if response.status != 200:
                        error_text = await response.text()
                        if response.status == 400 and 'TooManyRegister' in error_text:
                            error_data = json.loads(error_text)
                            delay_time = self.game['base_delay'] + random.uniform(5, 15) + random.uniform(1, 3)
                            logger.warning(
                                f'`{response.status}` ⚠️ | Game: `{self.game['name']}` | Proxy: `{ip}:{port})` | '
                                f'Error: `{error_data['error_code']}` ⏱️ | New delay: `{delay_time:.2f}`s.'
                            )
                            await asyncio.sleep(delay_time)
                            continue
                        else:
                            logger.warning(f'`{response.status}` ⚠️ | Game: ({self.game['name']} | '
                                           f'Proxy: {ip}:{port}): {error_text}')

                        await asyncio.sleep(random.uniform(3, 6))
                        continue

                    if 'application/json' in response.headers.get('Content-Type'):
                        data = await response.json()
                        if data.get('hasCode', False):
                            logger.info(
                                f'`{response.status}` ✅ | Event: `{self.game['name']}` | '
                                f'Proxy: `{ip}:{port}` successfully registered')
                            return True
                    else:
                        logger.warning(f'Unexpected response from the server: {await response.text()}')
                        await asyncio.sleep(5)
                        continue

            except Exception as error:
                logger.error(
                    f' ⚠️ Error in event registration `{self.game['name']}` | Proxy: `{ip}:{port}`: {error}')
                await asyncio.sleep(5)
        logger.error(f' ❌ Failed to register an event for `{self.game['name']}` | Proxy: {ip}:{port}, restart!')
        return False

    async def create_code(self):
        proxy = self.game['proxy']
        response = None
        parsed_url = urlparse(f'http://{proxy}')
        username = parsed_url.username
        password = parsed_url.password
        ip = parsed_url.hostname
        port = parsed_url.port
        auth = aiohttp.BasicAuth(username, password) if username and password else None
        while not response or not response.get('promoCode'):
            try:
                async with self.session.post(
                        'https://api.gamepromo.io/promo/create-code',
                        json={'promoId': self.game['promo_id']},
                        proxy=f'http://{proxy}',
                        proxy_auth=auth,
                        headers={
                            'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json; charset=utf-8',
                        }
                ) as resp:
                    response = await resp.json()
            except Exception as error:
                logger.error(f' ⚠️ Error creating code `{self.game['name']}` | Proxy: `{ip}:{port}` | `{error}`')
                await asyncio.sleep(random.uniform(1, 3.5))
        return response['promoCode']

    @staticmethod
    async def save_code_to_db(promo_code: str, game_name: str):
        try:
            formatted_game_name = game_name.replace(' ', '')
            async with async_session_maker() as session:
                await PromoCodeRepository.add_promo_code(session, PromoCodeCreateSchema(
                    game_name=formatted_game_name,
                    promo_code=promo_code))
                logger.info(f'🔑 `KEY` | `{promo_code[:12]}` | Saved in `promo_code` for game `{formatted_game_name}`')
        except Exception as e:
            logger.error(f'❌ Failed to save promo code `{promo_code[:12]}` for game `{game_name}`: {e}')

    async def gen_promo_code(self):
        await self.login_client()

        if await self.register_event():
            promo_code = await self.create_code()
            if promo_code:
                await self.save_code_to_db(promo_code, self.game['name'])
                return promo_code
        return None


async def gen(game):
    promo = GamePromo(game)

    try:
        while True:
            code_data = await promo.gen_promo_code()

            if code_data:
                await asyncio.sleep(random.uniform(0.1, 3) + 1)
    finally:
        await promo.close_session()
