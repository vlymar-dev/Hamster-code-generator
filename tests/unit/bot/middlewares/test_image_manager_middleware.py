import pytest


@pytest.mark.asyncio
async def test_image_manager_middleware_success(mock_image_manager_middleware, telegram_event, telegram_handler):
    data = {}

    await mock_image_manager_middleware(telegram_handler, telegram_event, data)

    assert 'image_manager' in data
    assert data['image_manager'] == mock_image_manager_middleware.image_manager

    telegram_handler.assert_awaited_once_with(telegram_event, data)


@pytest.mark.asyncio
async def test_image_manager_middleware_error(mock_image_manager_middleware, telegram_event, telegram_handler):
    error = Exception('Test error')
    telegram_handler.side_effect = error
    data = {}

    with pytest.raises(Exception) as exc_info:
        await mock_image_manager_middleware(telegram_handler, telegram_event, data)

    assert str(exc_info.value) == 'Test error'
    assert 'image_manager' in data
