from pathlib import Path
from random import choice

from aiogram.types import FSInputFile

from bot.common.static_data import SUPPORTED_EXTENSIONS


class ImageManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.categories: dict[str, list[Path]] = {}

    def load_category(self, name: str, subfolder: str) -> None:
        path = self.base_dir / 'uploads' / subfolder
        if not path.exists():
            print(f'Directory {path} not found')
            self.categories[name] = []

        images = [f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
        self.categories[name] = images

    def add_image(self, name: str, image_path: Path) -> None:
        if image_path.exists():
            self.categories.setdefault(name, []).append(image_path)

    def get_random_image(self, name: str) -> FSInputFile | None:
        images = self.categories.get(name, [])
        if not images:
            print(f'No images in category "{name}"')
            return None
        return FSInputFile(choice(images))
