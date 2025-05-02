from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.settings import (
    change_language_handler,
    notifications_handler,
    settings_menu_handler,
    subscribe_confirm_handler,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, expected_answer_photo_calls, expected_answer_calls',
    [
        ('fake_image_bytes', 1, 0),
        (None, 0, 1),
    ],
)
async def test_settings_menu_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    return_value,
    expected_answer_photo_calls,
    expected_answer_calls,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='settings_menu')

    mock_image_manager.get_random_image = MagicMock(return_value=return_value)

    await settings_menu_handler(callback_query=callback_query, image_manager=mock_image_manager)

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    assert callback_query.message.answer_photo.await_count == expected_answer_photo_calls
    assert callback_query.message.answer.await_count == expected_answer_calls
    mock_image_manager.get_random_image.assert_called_once_with('handlers')
    assert callback_query.data == 'settings_menu'


@pytest.mark.asyncio
async def test_settings_menu_handler_exception(
    telegram_user, telegram_chat, telegram_callback_query, mock_image_manager
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='settings_menu')

    mock_image_manager.get_random_image = MagicMock(side_effect=Exception('test error'))

    with pytest.raises(Exception) as exc_info:
        await settings_menu_handler(callback_query=callback_query, image_manager=mock_image_manager)

    assert str(exc_info.value) == 'test error'

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    mock_image_manager.get_random_image.assert_called_once_with('handlers')


@pytest.mark.asyncio
async def test_change_language_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    mock_cache_service,
    mock_session,
    monkeypatch,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='change_language')

    fake_language_data = SimpleNamespace(language_code='fr')
    monkeypatch.setattr(
        'bot.handlers.settings.UserCacheService.get_user_language', AsyncMock(return_value=fake_language_data)
    )

    await change_language_handler(callback_query, mock_session, mock_cache_service)

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    assert callback_query.data == 'change_language'


@pytest.mark.asyncio
async def test_change_language_handler_exception(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_cache_service,
    mock_session,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='settings_menu')

    callback_query.message.delete = AsyncMock(side_effect=Exception('Delete error'))

    with patch(
        'bot.handlers.settings.change_language_handler', new_callable=AsyncMock, side_effect=Exception('Delete error')
    ):
        with pytest.raises(Exception, match='Delete error'):
            await change_language_handler(callback_query, mock_session, mock_cache_service)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, expected_text_part',
    [
        (True, 'Subscribed'),
        (False, 'Unsubscribed'),
    ],
)
async def test_notifications_handler_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_cache_service,
    mock_session,
    monkeypatch,
    return_value,
    expected_text_part,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='notifications')

    monkeypatch.setattr('bot.handlers.settings.UserDAO.find_field_by_id', AsyncMock(return_value=return_value))

    await notifications_handler(callback_query, mock_session)
    called_text = callback_query.message.answer.call_args.kwargs.get('text')

    assert expected_text_part in called_text
    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    assert callback_query.data == 'notifications'


@pytest.mark.asyncio
async def test_notifications_handler_exception(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_session,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='notifications')

    callback_query.message.delete = AsyncMock(side_effect=Exception('Delete error'))

    with patch(
        'bot.handlers.settings.notifications_handler', new_callable=AsyncMock, side_effect=Exception('Delete error')
    ):
        with pytest.raises(Exception, match='Delete error'):
            await notifications_handler(callback_query, mock_session)


@pytest.mark.asyncio
@mock.patch('bot.handlers.settings.send_main_menu', new_callable=mock.AsyncMock)
async def test_subscribe_confirm_handler_success(
    mock_send_main_menu,
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    mock_session,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='subscribe_confirm')

    await subscribe_confirm_handler(callback_query, mock_session, mock_image_manager)

    callback_query.answer.assert_awaited_once()
    mock_send_main_menu.assert_awaited_once_with(callback_query, mock_session, mock_image_manager)
    assert callback_query.data == 'subscribe_confirm'


@pytest.mark.asyncio
async def test_subscribe_confirm_handler_exception(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_session,
    mock_image_manager,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='subscribe_confirm')

    callback_query.message.delete = AsyncMock(side_effect=Exception('Delete error'))

    with patch(
        'bot.handlers.settings.subscribe_confirm_handler', new_callable=AsyncMock, side_effect=Exception('Delete error')
    ):
        with pytest.raises(Exception, match='Delete error'):
            await subscribe_confirm_handler(callback_query, mock_session, mock_image_manager)
