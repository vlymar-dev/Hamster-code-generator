from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from bot.middlewares import CustomI18nMiddleware
from infrastructure.services import UserCacheService


@pytest.mark.asyncio
async def test_get_locale_from_cache_success(
    telegram_chat,
    telegram_user,
    telegram_message,
    mock_session,
    mock_cache_service,
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123))

    expected_locale = 'fr'
    fake_user_language = SimpleNamespace(language_code=expected_locale)

    with patch.object(UserCacheService, 'get_user_language', AsyncMock(return_value=fake_user_language)):
        middleware = CustomI18nMiddleware(path='bot/locales', default_locale='en', domain='messages')

        data = {
            'session_without_commit': mock_session,
            'cache_service': mock_cache_service,
        }

        locale = await middleware.get_locale(message, data)
        assert locale == expected_locale


@pytest.mark.asyncio
async def test_get_locale_no_user(telegram_chat, telegram_message):
    chat = telegram_chat
    message = telegram_message(chat, user=None)

    middleware = CustomI18nMiddleware(path='bot/locales', default_locale='en', domain='messages')

    locale = await middleware.get_locale(message, {})
    assert locale == 'en'


@pytest.mark.asyncio
async def test_get_locale_no_services(telegram_chat, telegram_user, telegram_message):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123))

    middleware = CustomI18nMiddleware(path='bot/locales', default_locale='en', domain='messages')

    locale = await middleware.get_locale(message, {})
    assert locale == 'en'


@pytest.mark.asyncio
async def test_get_locale_exception_during_language_fetch(
    telegram_chat,
    telegram_user,
    telegram_message,
    mock_session,
    mock_cache_service,
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123))

    with patch.object(UserCacheService, 'get_user_language', AsyncMock(side_effect=Exception('DB error'))):
        middleware = CustomI18nMiddleware(path='bot/locales', default_locale='en', domain='messages')

        data = {
            'session_without_commit': mock_session,
            'cache_service': mock_cache_service,
        }

        locale = await middleware.get_locale(message, data)
        assert locale == 'en'
