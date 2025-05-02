import pytest

from bot.middlewares import CacheServiceMiddleware, ImageManagerMiddleware
from bot.middlewares.database_middleware import (
    BaseDatabaseMiddleware,
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)


@pytest.fixture
def mock_cache_service_middleware(mock_cache_service) -> CacheServiceMiddleware:
    return CacheServiceMiddleware(mock_cache_service)


@pytest.fixture
def mock_image_manager_middleware(mock_image_manager) -> ImageManagerMiddleware:
    return ImageManagerMiddleware(mock_image_manager)


@pytest.fixture
def mock_base_database_middleware() -> BaseDatabaseMiddleware:
    return BaseDatabaseMiddleware()


@pytest.fixture
def mock_database_middleware_with_commit() -> DatabaseMiddlewareWithCommit:
    return DatabaseMiddlewareWithCommit()


@pytest.fixture
def mock_database_middleware_without_commit() -> DatabaseMiddlewareWithoutCommit:
    return DatabaseMiddlewareWithoutCommit()
