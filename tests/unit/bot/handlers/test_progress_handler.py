from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.progress import ProgresText, user_progress_handler
from tests.unit.bot.handlers.conftest import FakeProgress


@pytest.mark.asyncio
async def test_user_progress_handler_no_data(
    telegram_user, telegram_chat, telegram_callback_query, mock_image_manager, mock_session, monkeypatch
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='user_progress')
    monkeypatch.setattr('bot.handlers.progress.progres_service.get_user_progres', AsyncMock(return_value=None))

    await user_progress_handler(
        callback_query=callback_query, session_with_commit=mock_session, image_manager=mock_image_manager
    )

    callback_query.answer.assert_awaited_once_with(text='User data not found.', show_alert=True)
    callback_query.message.delete.assert_not_awaited()
    callback_query.message.answer_photo.assert_not_awaited()
    callback_query.message.answer.assert_not_awaited()
    assert callback_query.data == 'user_progress'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'return_value, expected_answer_photo_calls, expected_answer_calls',
    [
        ('fake_image_bytes', 1, 0),
        (None, 0, 1),
    ],
)
async def test_user_progress_handler_success(
    telegram_user,
    telegram_chat,
    telegram_callback_query,
    mock_image_manager,
    return_value,
    expected_answer_photo_calls,
    expected_answer_calls,
    mock_session,
    monkeypatch,
):
    user = telegram_user(123)
    callback_query = telegram_callback_query(chat=telegram_chat, user=user, data='user_progress')
    fake_prog = FakeProgress()

    monkeypatch.setattr('bot.handlers.progress.progres_service.get_user_progres', AsyncMock(return_value=fake_prog))
    mock_image_manager.get_random_image = MagicMock(return_value=return_value)

    with patch('bot.handlers.progress.get_progress_keyboard', return_value='keyboard') as mock_kb:
        await user_progress_handler(
            callback_query=callback_query, session_with_commit=mock_session, image_manager=mock_image_manager
        )

        callback_query.message.delete.assert_awaited_once()
        callback_query.answer.assert_awaited_once()
        assert callback_query.message.answer_photo.await_count == expected_answer_photo_calls
        assert callback_query.message.answer.await_count == expected_answer_calls
        mock_image_manager.get_random_image.assert_called_once_with('handlers')
        mock_kb.assert_called_once_with(user_id=user.id)


@pytest.mark.asyncio
async def test_user_progress_handler_exception(
    telegram_user, telegram_chat, telegram_callback_query, mock_image_manager, monkeypatch, mock_session
):
    callback_query = telegram_callback_query(chat=telegram_chat, user=telegram_user(123), data='user_progress')
    fake_prog = FakeProgress()

    monkeypatch.setattr('bot.handlers.progress.progres_service.get_user_progres', AsyncMock(return_value=fake_prog))

    mock_image_manager.get_random_image = MagicMock(side_effect=Exception('test error'))

    with pytest.raises(Exception) as exc_info:
        await user_progress_handler(
            callback_query=callback_query, session_with_commit=mock_session, image_manager=mock_image_manager
        )

    assert str(exc_info.value) == 'test error'

    mock_image_manager.get_random_image.assert_called_once_with('handlers')


def test_get_achievement_text_known_key():
    pt = ProgresText('adventurer', 'free')
    text = pt.get_achievement_text()
    assert 'Adventurer' in text


def test_get_achievement_text_default():
    pt = ProgresText('unknown_key', 'free')
    text = pt.get_achievement_text()
    assert 'Newcomer' in text


def test_get_status_text_known_key():
    pt = ProgresText('newcomer', 'premium')
    text = pt.get_status_text()
    assert 'Elite Player' in text or 'Elite Player!' in text


def test_get_status_text_default():
    pt = ProgresText('newcomer', 'unknown')
    text = pt.get_status_text()
    assert 'Regular Player' in text


def test_format_progress_with_next_level():
    assert ProgresText.format_progress('5/10', 'next') == '5/10'


def test_format_progress_max_level():
    assert ProgresText.format_progress('5/10', None) == 'Max level achieved ✔️'
