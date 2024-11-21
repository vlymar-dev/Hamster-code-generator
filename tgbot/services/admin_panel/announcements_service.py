import os
import uuid
from io import BytesIO
from typing import Optional

import aiofiles
from aiogram import Bot
from aiogram.types import PhotoSize
from PIL import Image, UnidentifiedImageError

from infrastructure.models.announcement_model import Announcement, AnnouncementTranslation
from infrastructure.repositories.announcement_repo import AnnouncementRepository


class AnnouncementService:

    @staticmethod
    async def show_announcements_with_languages(announcement_repo: AnnouncementRepository) -> list[dict]:
        return await announcement_repo.get_all_announcements_with_languages()


    @staticmethod
    async def process_and_save_image(photo: PhotoSize, bot: Bot) -> str:
        filename = f'{uuid.uuid4()}.webp'
        image_dir = 'uploads/announcement_images'
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, filename)

        try:
            file = await bot.download(photo.file_id)
            file.seek(0)

            with Image.open(file) as image:
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")

                output_io = BytesIO()
                image.save(output_io, format='WEBP', quality=85, optimize=True)
                output_io.seek(0)

                async with aiofiles.open(image_path, 'wb') as file:
                    await file.write(output_io.getvalue())
        except UnidentifiedImageError:
                raise ValueError("The provided file is not a supported image.")
        finally:
            await file.close()
        image_url = os.path.join('uploads/announcement_images', filename)
        return image_url


    @staticmethod
    async def create_announcement_without_text_translation(title: str, created_by: int, announcement_repo: AnnouncementRepository,
                                  image_url: str = None,) -> Announcement:
        new_announcement = Announcement(
            title=title,
            image_url=image_url,
            created_by=created_by
        )
        await announcement_repo.add_announcement(new_announcement)
        return new_announcement

    @staticmethod
    async def create_translation_for_announcement(announcement_id: int, language_code: str, text: str,
                                                  announcement_repo: AnnouncementRepository) -> AnnouncementTranslation:
        new_translation = AnnouncementTranslation(
            announcement_id=announcement_id,
            language_code=language_code,
            text=text,
        )
        try:
            return await announcement_repo.add_translation_if_exists(new_translation)
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    async def get_announcement_details(announcement_id: int, announcement_repo: AnnouncementRepository) -> tuple:
        announcement = await announcement_repo.get_announcement_or_error(announcement_id)

        english_text = next(
            (translation.text for translation in announcement.translations_text if translation.language_code == 'en'),
            None
        )
        language_codes = [translation.language_code for translation in announcement.translations_text]

        return announcement.title, english_text, language_codes, announcement.image_url

    @staticmethod
    async def delete_announcement(announcement_id: int, announcement_repo: AnnouncementRepository) -> None:
        try:
            await announcement_repo.delete_announcement_with_translations(announcement_id)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while deleting announcement: {e}")

    @staticmethod
    def filter_languages(languages: dict, text_languages: list[str], include: bool) -> dict:
        """
            Filters languages based on their presence in the `text_languages` list.

            Args:
                languages (dict): A dictionary of all available languages (code -> name).
                text_languages (list[str]): A list of language codes to compare against.
                include (bool): If True, return languages present in `text_languages`.
                                If False, return languages not present in `text_languages`.

            Returns:
                dict: A filtered dictionary of languages based on the `include` parameter.
            """
        if include:
            return {key: value for key, value in languages.items() if key in text_languages}
        else:
            return {key: value for key, value in languages.items() if key not in text_languages}

    @staticmethod
    async def get_translation_for_language(announcement_id: int, language_code: str,
                                           announcement_repo: AnnouncementRepository) -> Optional[str]:
        translation = await announcement_repo.get_translation(announcement_id, language_code)
        if translation:
            return translation.text
        return None

    @staticmethod
    async def update_translation_for_announcement(announcement_id: int, language_code: str, text: str,
                                                  announcement_repo: AnnouncementRepository) -> AnnouncementTranslation:
        try:
            translation = AnnouncementTranslation(
                announcement_id=announcement_id,
                language_code=language_code,
                text=text
            )
            return await announcement_repo.upsert_translation(translation)
        except ValueError as e:
            raise ValueError(f'Failed to create or update translation: {e}')