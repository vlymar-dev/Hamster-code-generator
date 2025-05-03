from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.commands import admin_command, change_language_command, handle_start_command, paysupport_command
from infrastructure.services import UserService


@pytest.mark.asyncio
async def test_handle_start_command_success_with_image(
    telegram_user, telegram_chat, telegram_message, mock_session, aiogram_bot, mock_image_manager
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/start')

    mock_image_manager.get_random_image = MagicMock(return_value='some_image_bytes')

    with (
        patch.object(UserService, 'user_registration', new_callable=AsyncMock) as mock_user_registration,
        patch.object(UserService, 'referral_adding', new_callable=AsyncMock) as mock_referral_adding,
    ):
        mock_user_registration.return_value = True
        mock_referral_adding.return_value = False

        await handle_start_command(
            message=message, session_with_commit=mock_session, bot=aiogram_bot, image_manager=mock_image_manager
        )

        mock_user_registration.assert_awaited_once()
        mock_referral_adding.assert_not_awaited()
        message.answer_photo.assert_awaited_once()
        assert message.text == '/start'


@pytest.mark.asyncio
async def test_handle_start_command_success_with_referral(
    telegram_user, telegram_chat, telegram_message, mock_session, aiogram_bot, mock_image_manager
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/start 456')

    mock_image_manager.get_random_image = MagicMock(return_value='some_image_bytes')

    with (
        patch.object(UserService, 'user_registration', new_callable=AsyncMock) as mock_user_registration,
        patch.object(UserService, 'referral_adding', new_callable=AsyncMock) as mock_referral_adding,
    ):
        mock_user_registration.return_value = True
        mock_referral_adding.return_value = True

        await handle_start_command(
            message=message, session_with_commit=mock_session, bot=aiogram_bot, image_manager=mock_image_manager
        )

        mock_user_registration.assert_awaited_once()
        mock_referral_adding.assert_awaited_once_with(session=mock_session, referrer_id=456, referred_id=123)
        mock_image_manager.get_random_image.assert_called_once_with('handlers')
        message.answer_photo.assert_awaited_once()
        aiogram_bot.send_message.assert_awaited_once()
        assert message.text == '/start 456'


@pytest.mark.asyncio
async def test_change_language_command_success(
    telegram_user, telegram_message, telegram_chat, mock_session, mock_image_manager, mock_cache_service
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/change_language')

    with patch('bot.handlers.commands.UserCacheService.get_user_language', new_callable=AsyncMock) as mock_get_language:
        mock_get_language.return_value = MagicMock(language_code='en')

        await change_language_command(
            message=message,
            session_without_commit=mock_session,
            cache_service=mock_cache_service,
        )

        mock_get_language.assert_awaited_once()
        message.answer.assert_awaited_once()
        args, kwargs = message.answer.call_args
        assert 'Please choose a language:' in kwargs['text']
        assert message.text == '/change_language'


@pytest.mark.asyncio
async def test_change_language_command_exception(
    telegram_user, telegram_message, telegram_chat, mock_session, mock_image_manager, mock_cache_service
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/change_language')

    with patch(
        'bot.handlers.commands.UserCacheService.get_user_language',
        new_callable=AsyncMock,
        side_effect=Exception('Language error'),
    ):
        with pytest.raises(Exception, match='Language error'):
            await change_language_command(
                message=message,
                session_without_commit=mock_session,
                cache_service=mock_cache_service,
            )

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_paysupport_command_success(telegram_chat, telegram_message, telegram_user, is_banned_filter):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/paysupport')

    await paysupport_command(message=message)

    message.delete.assert_awaited_once()
    message.answer.assert_awaited_once()
    args, kwargs = message.answer.call_args
    assert 'Your donation helps us' in kwargs['text']
    assert message.text == '/paysupport'


@pytest.mark.asyncio
async def test_paysupport_command_exception(telegram_chat, telegram_message, telegram_user, is_banned_filter):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/paysupport')

    message.delete = AsyncMock(side_effect=Exception('Delete error'))

    with pytest.raises(Exception, match='Delete error'):
        await paysupport_command(message=message)

    message.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_command_success(telegram_user, telegram_chat, telegram_message, admin_filter, is_banned_filter):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/admin')

    with patch('bot.handlers.commands.show_admin_panel', new_callable=AsyncMock) as mock_show_admin_panel:
        await admin_command(message=message)

        mock_show_admin_panel.assert_awaited_once_with(message)
        assert message.text == '/admin'


@pytest.mark.asyncio
async def test_admin_command_exception(telegram_user, telegram_chat, telegram_message, admin_filter, is_banned_filter):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123), text='/admin')

    message.delete = AsyncMock(side_effect=Exception('Delete error'))

    with patch('bot.handlers.commands.show_admin_panel', new_callable=AsyncMock, side_effect=Exception('Admin error')):
        with pytest.raises(Exception, match='Admin error'):
            await admin_command(message=message)
