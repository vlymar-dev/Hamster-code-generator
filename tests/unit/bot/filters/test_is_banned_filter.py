from types import SimpleNamespace

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user_id, mock_is_banned, expected, should_call_answer',
    [
        pytest.param(None, None, False, False, id='Not user_id'),
        pytest.param(12345, True, False, True, id='Is banned'),
        pytest.param(54321, False, True, False, id='Not banned'),
    ],
)
@pytest.mark.parametrize(
    'object_type',
    [
        pytest.param('message', id='Message test'),
        pytest.param('callback', id='Callback test'),
    ],
)
async def test_is_banned_filter(
    is_banned_filter,
    telegram_message,
    telegram_callback_query,
    telegram_user,
    telegram_chat,
    mock_session,
    mock_cache_service,
    user_id,
    mock_is_banned,
    expected,
    should_call_answer,
    object_type,
):
    user = telegram_user(user_id)
    if object_type == 'message':
        obj = telegram_message(telegram_chat, user)
    else:
        obj = telegram_callback_query(telegram_chat, user)

    mock_cache_service.get_or_set.return_value = SimpleNamespace(is_banned=mock_is_banned)

    result = await is_banned_filter(obj, mock_session, mock_cache_service)

    assert result == expected
    if should_call_answer:
        obj.answer.assert_called_once()
    else:
        obj.answer.assert_not_called()
