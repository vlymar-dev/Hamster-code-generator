from pathlib import Path

import pytest

from bot.utils import ImageManager


@pytest.fixture
def image_manager(tmp_path: Path) -> ImageManager:
    return ImageManager(base_dir=tmp_path)


@pytest.fixture
def test_image(tmp_path: Path) -> Path:
    image_path = tmp_path / 'test.png'
    image_path.touch()
    return image_path
