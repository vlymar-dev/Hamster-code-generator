import logging
from pathlib import Path
from random import choice

from aiogram.types import FSInputFile

from bot.common.static_data import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class ImageManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.categories: dict[str, list[Path]] = {}

    def load_category(self, name: str, subfolder: str) -> None:
        path = self.base_dir / 'var' / 'storage' / 'uploads' / subfolder
        if not path.exists():
            logger.error(f'Directory {path} not found for category "{name}"')
            self.categories[name] = []
            return

        try:
            images = [f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
            if not images:
                logger.warning(f'No supported images found in {path} for category "{name}"')
            self.categories[name] = images
        except Exception as e:
            logger.error(f'Error accessing directory {path}: {str(e)}')
            self.categories[name] = []

    def add_image(self, name: str, image_path: Path) -> None:
        if not image_path.exists():
            logger.warning(f'Attempted to add non-existent image: {image_path} to category "{name}"')
            return
        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning(f'Unsupported file format: {image_path} for category "{name}"')
            return

        self.categories.setdefault(name, []).append(image_path)
        logger.debug(f'Added image {image_path.name} to category "{name}"')

    def get_random_image(self, name: str) -> FSInputFile | None:
        images = self.categories.get(name, [])
        if not images:
            logger.warning(f'Attempt to get image from empty category: "{name}"')
            return None
        selected = choice(images)
        logger.debug(f'Selected image {selected.name} from category "{name}"')
        return FSInputFile(selected)
