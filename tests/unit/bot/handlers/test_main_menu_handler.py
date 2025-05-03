from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from bot.handlers.main_menu import back_to_main_menu_handler, send_main_menu


@pytest.mark.asyncio
async def test_back_to_main_menu_handler_success(
    telegram_user, telegram_chat, telegram_callback_query, mock_session, telegram_state, mock_image_manager
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='back_to_main_menu')
    with patch('bot.handlers.main_menu.send_main_menu', new_callable=AsyncMock) as mock_send:
        await back_to_main_menu_handler(
            callback_query=callback_query,
            session_without_commit=mock_session,
            state=telegram_state,
            image_manager=mock_image_manager,
        )

        mock_send.assert_awaited_once_with(callback_query, mock_session, mock_image_manager)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, is_callback, expected_photo, expected_answer',
    [
        ('fake_image_bytes', True, 1, 0),
        (None, True, 0, 1),
        ('fake_image_bytes', False, 1, 0),
        (None, False, 0, 1),
    ],
)
async def test_send_main_menu_variants(
    telegram_user,
    telegram_chat,
    telegram_message,
    telegram_callback_query,
    mock_session,
    mock_image_manager,
    monkeypatch,
    return_value,
    is_callback,
    expected_photo,
    expected_answer,
):
    user = telegram_user(321)
    if is_callback:
        event = telegram_callback_query(chat=telegram_chat, user=user)
        event.message.delete = AsyncMock()
        event.message.answer_photo = AsyncMock()
        event.message.answer = AsyncMock()
    else:
        event = telegram_message(chat=telegram_chat, user=user)
        event.delete = AsyncMock()
        event.answer_photo = AsyncMock()
        event.answer = AsyncMock()

    mock_image_manager.get_random_image = MagicMock(return_value=return_value)
    monkeypatch.setattr('bot.handlers.main_menu.UserDAO.find_today_keys_count', AsyncMock(return_value=5))
    monkeypatch.setattr('bot.handlers.main_menu.config.telegram.POPULARITY_COEFFICIENT', 2)
    monkeypatch.setattr('bot.handlers.main_menu.get_main_menu_kb', lambda: 'kb_menu')

    await send_main_menu(event, mock_session, mock_image_manager)

    if is_callback:
        event.message.delete.assert_awaited_once()
        assert event.message.answer_photo.await_count == expected_photo
        assert event.message.answer.await_count == expected_answer
    else:
        event.delete.assert_awaited_once()
        assert event.answer_photo.await_count == expected_photo
        assert event.answer.await_count == expected_answer

    mock_image_manager.get_random_image.assert_called_once_with('handlers')
    UserDAO = __import__('bot.handlers.main_menu', fromlist=['UserDAO']).UserDAO
    UserDAO.find_today_keys_count.assert_awaited_once_with(mock_session)  # noqa

    if expected_photo:
        if is_callback:
            event.message.answer_photo.assert_awaited_once_with(photo=ANY, caption=ANY, reply_markup='kb_menu')
        else:
            event.answer_photo.assert_awaited_once_with(photo=ANY, caption=ANY, reply_markup='kb_menu')
    else:
        if is_callback:
            event.message.answer.assert_awaited_once_with(text=ANY, reply_markup='kb_menu')
        else:
            event.answer.assert_awaited_once_with(text=ANY, reply_markup='kb_menu')


@pytest.mark.asyncio
async def test_send_main_menu_exception(
    telegram_user, telegram_chat, telegram_callback_query, mock_session, mock_image_manager, monkeypatch
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(321))
    callback_query.message.delete = AsyncMock()
    callback_query.answer = AsyncMock()
    mock_image_manager.get_random_image = MagicMock(side_effect=Exception('fail'))

    with pytest.raises(Exception, match='fail'):
        await send_main_menu(callback_query, mock_session, mock_image_manager)

    mock_image_manager.get_random_image.assert_called_once_with('handlers')
