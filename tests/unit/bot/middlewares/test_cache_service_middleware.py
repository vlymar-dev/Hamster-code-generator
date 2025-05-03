import logging
from unittest.mock import MagicMock

import pytest
from aiogram.types import TelegramObject


@pytest.fixture
def dummy_event():
    """Creates a dummy TelegramObject event."""
    return MagicMock(spec=TelegramObject)


@pytest.mark.asyncio
async def test_cache_service_injected_and_handler_called(mock_cache_service_middleware, dummy_event, caplog):
    """
    Given a handler that returns a value, the middleware should inject the cache_service
    into the data dict, call the handler, and return its result.
    """
    caplog.set_level(logging.DEBUG)

    async def handler(event, data):
        # The middleware must have set cache_service on data
        from infrastructure.services import CacheService

        assert isinstance(data.get('cache_service'), CacheService)
        # Return a sentinel result
        return 'handler_result'

    result = await mock_cache_service_middleware(handler, dummy_event, {})

    assert result == 'handler_result'
    assert 'Injecting cache service into handler' in caplog.text


@pytest.mark.asyncio
async def test_cache_service_middleware_propagates_errors_and_logs(mock_cache_service_middleware, dummy_event, caplog):
    """
    If the handler raises an exception, the middleware should log an error and re-raise it.
    """
    caplog.set_level(logging.ERROR)

    async def handler(event, data):
        raise RuntimeError('Unexpected failure')

    with pytest.raises(RuntimeError, match='Unexpected failure'):
        await mock_cache_service_middleware(handler, dummy_event, {})

    # Verify that the error was logged with the correct message
    assert 'CacheServiceMiddleware error: Unexpected failure' in caplog.text
