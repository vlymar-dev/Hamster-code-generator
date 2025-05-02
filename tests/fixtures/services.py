from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from bot.utils import ImageManager
from infrastructure.services import CacheService


@pytest.fixture
def mock_cache_service():
    """Mock CacheService with async methods."""
    mock = AsyncMock(spec=CacheService, autospec=True)
    mock.get_or_set = AsyncMock()
    return mock


@pytest.fixture
def mock_image_manager(tmp_path: Path) -> ImageManager:
    """ImageManager with test directory structure."""
    test_dir = tmp_path / 'var/storage/uploads/test_category'
    test_dir.mkdir(parents=True, exist_ok=True)

    for i in range(3):
        (test_dir / f'test_image_{i}.png').touch()

    manager = ImageManager(tmp_path)
    manager.load_category('test', 'test_category')
    return manager
