from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

pytest_plugins = [
    'tests.fixtures.telegram',
    'tests.fixtures.services',
]


@pytest.fixture
def aiogram_bot():
    """Mock AIOGram Bot instance."""
    aiogram_bot.send_message = AsyncMock()
    return aiogram_bot


@pytest.fixture
def mock_session() -> AsyncMock:
    """Mock AsyncSession with database methods."""
    session = MagicMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture(autouse=True)
def disable_i18n():
    """Disable i18n for all tests to avoid translation lookups."""
    fake_i18n = MagicMock()
    fake_i18n.gettext.side_effect = lambda s: s  # returns a string
    with patch('aiogram.utils.i18n.context.get_i18n', return_value=fake_i18n):
        yield
