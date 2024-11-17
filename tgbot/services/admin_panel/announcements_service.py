import os
import uuid
from io import BytesIO

import aiofiles
from aiogram import Bot
from aiogram.types import PhotoSize
from PIL import Image, UnidentifiedImageError

from infrastructure.models.announcement_model import Announcement
from infrastructure.repositories.announcement_repo import AnnouncementRepository


class AnnouncementService:

    @staticmethod
    async def show_announcements( announcement_repo: AnnouncementRepository) -> list[Announcement]:
        announcements = await announcement_repo.get_all_announcements()
        return announcements


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
        image_url = os.path.join('announcement_images', filename)
        return image_url


    @staticmethod
    async def create_announcement(title: str, text: str, created_by: int, announcement_repo: AnnouncementRepository,
                                  image_url: str = None,) -> Announcement:
        new_announcement = Announcement(
            title=title,
            text=text,
            image_url=image_url,
            created_by=created_by
        )
        await announcement_repo.add_announcement(new_announcement)
        return new_announcement
