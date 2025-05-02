from types import SimpleNamespace

import pytest

from infrastructure import config


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user_id, config_ids, mock_role, expected, should_call_answer',
    [
        pytest.param(12345, [12345], None, True, False, id='Admin config'),
        pytest.param(1111, [], 'admin', True, False, id='Admin from DB'),
        pytest.param(54321, [], 'user', False, True, id='Non-admin user'),
    ],
)
async def test_admin_filter(
    admin_filter,
    mock_session,
    mock_cache_service,
    monkeypatch,
    user_id,
    config_ids,
    mock_role,
    expected,
    should_call_answer,
    telegram_user,
    telegram_message,
    telegram_chat,
):
    user = telegram_user(user_id)
    message = telegram_message(telegram_chat, user)

    monkeypatch.setattr(config.telegram, 'ADMIN_ACCESS_IDs', [12345])
    mock_cache_service.get_or_set.return_value = SimpleNamespace(user_role=mock_role) if mock_role else None

    result = await admin_filter(message, mock_session, mock_cache_service)

    assert result == expected
    if should_call_answer:
        message.answer.assert_called_once()
    else:
        message.answer.assert_not_called()
