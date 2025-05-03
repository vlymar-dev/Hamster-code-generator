import pytest


@pytest.mark.asyncio
async def test_base_middleware_raises_not_implemented(
    telegram_message, telegram_chat, telegram_user, telegram_handler, mock_base_database_middleware
):
    message = telegram_message(chat=telegram_chat, user=telegram_user(123))

    with pytest.raises(NotImplementedError):
        await mock_base_database_middleware(telegram_handler, message, {})


@pytest.mark.asyncio
async def test_database_middleware_without_commit(
    telegram_message, telegram_chat, telegram_user, mock_session, mock_database_middleware_without_commit
):
    user = telegram_user(12345)
    chat = telegram_chat
    message = telegram_message(chat, user)

    async def handler(msg, data):
        return True

    await mock_database_middleware_without_commit(handler, message, {})

    mock_session.commit.assert_not_called()
