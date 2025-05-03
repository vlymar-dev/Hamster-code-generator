from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, Message, User

from bot.filters import AdminFilter, IsBannedFilter


@pytest.fixture
def telegram_user():
    """Generate mock Telegram User with given ID."""

    def _telegram_user(user_id: int) -> User:
        user = MagicMock(spec=User)
        user.id = user_id
        user.is_bot = False
        user.first_name = 'Test'
        user.last_name = 'User'
        user.username = 'test'
        user.language_code = 'fr'
        return user

    return _telegram_user


@pytest.fixture
def telegram_chat() -> Chat:
    """Generate mock private Chat."""
    chat = MagicMock(spec=Chat)
    chat.id = 12
    chat.type = 'private'
    return chat


@pytest.fixture
def telegram_message():
    """Generate mock Message with optional text."""

    def _telegram_message(chat: Chat, user: User, text: str | None = None) -> Message:
        message = MagicMock(spec=Message)
        message.message_id = 1
        message.from_user = user
        message.chat = chat
        message.text = text
        message.date = datetime.now()
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()
        message.delete = AsyncMock()
        message.react = AsyncMock()
        return message

    return _telegram_message


@pytest.fixture
def telegram_callback_query():
    """Generate mock CallbackQuery with optional data."""

    def _telegram_callback_query(chat: Chat, user: User, data: str | None = None) -> CallbackQuery:
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.callback_query_id = 1
        callback_query.from_user = user
        callback_query.chat_instance = chat
        callback_query.data = data
        callback_query.message = MagicMock()
        callback_query.answer = AsyncMock()
        callback_query.message.answer = AsyncMock()
        callback_query.message.delete = AsyncMock()
        callback_query.message.answer_photo = AsyncMock()
        return callback_query

    return _telegram_callback_query


@pytest.fixture
def telegram_event() -> MagicMock:
    """Generic mock Telegram event."""
    event = MagicMock()
    event.event_type = 'test_event'
    return event


@pytest.fixture
def telegram_handler() -> AsyncMock:
    """Mock async handler function."""
    return AsyncMock()


@pytest.fixture
def telegram_state() -> FSMContext:
    """Mock FSMContext for state management."""
    state = MagicMock(spec=FSMContext)
    state.clear = AsyncMock()
    return state


@pytest.fixture
def admin_filter():
    """AdminFilter instance."""
    return AdminFilter()


@pytest.fixture
def is_banned_filter():
    """IsBannedFilter instance."""
    return IsBannedFilter()
