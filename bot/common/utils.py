from datetime import date, datetime
from random import choice

from aiogram.types import FSInputFile

from core import BASE_DIR


def get_current_time() -> datetime:
    return datetime.now()


def get_current_date() -> date:
    return datetime.now().date()


def get_random_image(subfolder: str, specific_image: str = None) -> FSInputFile | None:
    try:
        base_images_folder = BASE_DIR / 'uploads' / 'handlers_images'
        target_folder = base_images_folder / subfolder
        supported_extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp')

        if not target_folder.exists() or not target_folder.is_dir():
            print(f'Directory {target_folder} does not exist or is not a directory.')
            return None

        images = [f for f in target_folder.iterdir() if f.suffix.lower() in supported_extensions]
        if specific_image:
            matching_files = [f for f in images if f.stem == specific_image]
            if not matching_files:
                print(f'The file {specific_image} with supported extensions {supported_extensions} '
                      f'is not found in the {target_folder} folder.')
                return None
            image_path = target_folder / matching_files[0]
        else:
            if not images:
                print(f'No images found in the {target_folder} folder.')
                return None
            image_path = target_folder / choice(images)

        return FSInputFile(image_path)

    except Exception as e:
        print(f'Error when loading an image: {e}')
        return None
