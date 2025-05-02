from unittest.mock import MagicMock

import pytest

from bot.handlers.feedback import process_user_feedback_message, start_feedback_handler


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, expected_answer_photo_calls, expected_answer_calls',
    [
        ('fake_image_bytes', 1, 0),
        (None, 0, 1),
    ],
)
async def test_start_feedback_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    telegram_state,
    return_value,
    expected_answer_photo_calls,
    expected_answer_calls,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='feedback')

    mock_image_manager.get_random_image = MagicMock(return_value=return_value)

    await start_feedback_handler(callback_query=callback_query, image_manager=mock_image_manager, state=telegram_state)

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    assert callback_query.message.answer_photo.await_count == expected_answer_photo_calls
    assert callback_query.message.answer.await_count == expected_answer_calls
    mock_image_manager.get_random_image.assert_called_once_with('handlers')
    assert callback_query.data == 'feedback'


@pytest.mark.asyncio
async def test_start_feedback_handler_exception(
    telegram_user, telegram_chat, telegram_callback_query, mock_image_manager, telegram_state
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='feedback')

    mock_image_manager.get_random_image = MagicMock(side_effect=Exception('test error'))

    with pytest.raises(Exception) as exc_info:
        await start_feedback_handler(
            callback_query=callback_query, image_manager=mock_image_manager, state=telegram_state
        )

    assert str(exc_info.value) == 'test error'

    mock_image_manager.get_random_image.assert_called_once_with('handlers')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'text, return_value, expect_notify, expect_photo, expect_answer',
    [
        ('A', None, False, 0, 0),
        ('Great bot!', 'fake_image_bytes', True, 1, 0),
        ('Another message', None, True, 0, 1),
    ],
)
async def test_process_user_feedback_message_success(
    telegram_user,
    telegram_chat,
    telegram_message,
    telegram_callback_query,
    mock_image_manager,
    telegram_state,
    aiogram_bot,
    text,
    return_value,
    expect_notify,
    expect_photo,
    expect_answer,
    monkeypatch,
):
    user = telegram_user(123)
    message = telegram_message(chat=telegram_chat, user=user, text=text)

    monkeypatch.setattr('bot.handlers.feedback.config.telegram.ADMIN_ACCESS_IDs', [111])
    monkeypatch.setattr('bot.handlers.feedback.get_back_to_main_menu_keyboard', lambda: 'kb_back')
    monkeypatch.setattr('bot.handlers.feedback.get_admin_feedback_kb', lambda user_id, message_id: 'kb_admin')
    mock_image_manager.get_random_image = MagicMock(return_value=return_value)

    await process_user_feedback_message(message, aiogram_bot, mock_image_manager)

    if len(text) < 2:
        message.answer_photo.assert_not_awaited()
        message.answer.assert_not_awaited()
        aiogram_bot.send_message.assert_not_awaited()
        message.react.assert_not_awaited()
        return

    if return_value:
        message.answer_photo.assert_awaited_once_with(
            photo=return_value,
            caption='💖 Thank you for your feedback!\nWe really appreciate you taking the time to share your thoughts with us. 💕',
            reply_markup='kb_back',
        )
    else:
        message.answer.assert_awaited_once_with(
            text='💖 Thank you for your feedback!\nWe really appreciate you taking the time to share your thoughts with us. 💕',
            reply_markup='kb_back',
        )

    if expect_notify:
        aiogram_bot.send_message.assert_awaited_once_with(
            chat_id=111,
            text=(
                '📨 New feedback received!\n\nFrom: {username}\n'.format(username=user.username)
                + 'Message:\n\n{text}'.format(text=text)
            ),
            reply_markup='kb_admin',
        )
        message.react.assert_awaited_once()
    else:
        aiogram_bot.send_message.assert_not_awaited()
        message.react.assert_not_awaited()
