from unittest.mock import MagicMock

import pytest

from bot.handlers.referral_links import referral_links_handler


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, expected_answer_photo_calls, expected_answer_calls',
    [
        ('fake_image_bytes', 1, 0),
        (None, 0, 1),
    ],
)
async def test_referral_links_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    return_value,
    expected_answer_photo_calls,
    expected_answer_calls,
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='referral_links')

    mock_image_manager.get_random_image = MagicMock(return_value=return_value)

    await referral_links_handler(callback_query=callback_query, image_manager=mock_image_manager)

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    assert callback_query.message.answer_photo.await_count == expected_answer_photo_calls
    assert callback_query.message.answer.await_count == expected_answer_calls
    mock_image_manager.get_random_image.assert_called_once_with('handlers')
    assert callback_query.data == 'referral_links'


@pytest.mark.asyncio
async def test_referral_links_handler_exception(
    telegram_user, telegram_chat, telegram_callback_query, mock_image_manager
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='referral_links')

    mock_image_manager.get_random_image = MagicMock(side_effect=Exception('test error'))

    with pytest.raises(Exception) as exc_info:
        await referral_links_handler(callback_query=callback_query, image_manager=mock_image_manager)

    assert str(exc_info.value) == 'test error'

    callback_query.message.delete.assert_awaited_once()
    callback_query.answer.assert_awaited_once()
    mock_image_manager.get_random_image.assert_called_once_with('handlers')
