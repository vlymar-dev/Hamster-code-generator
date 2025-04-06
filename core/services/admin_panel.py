import uuid
from io import BytesIO
from pathlib import Path

import aiofiles
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import FSInputFile, PhotoSize
from PIL import Image, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BASE_DIR, config
from db.repositories import AnnouncementRepository, UserRepository


class AdminPanelService:

    @staticmethod
    async def process_and_save_image(photo: PhotoSize, bot: Bot) -> str:
        filename = f'{uuid.uuid4()}.webp'
        image_dir = BASE_DIR / 'uploads' / 'announcement_images'
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / filename

        try:
            file = await bot.download(photo.file_id)
            file.seek(0)

            with Image.open(file) as image:
                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGB')

                output_io = BytesIO()
                image.save(output_io, format='WEBP', quality=85, optimize=True)
                output_io.seek(0)

                async with aiofiles.open(image_path, 'wb') as file:
                    await file.write(output_io.getvalue())
        except UnidentifiedImageError:
                raise ValueError('The provided file is not a supported image.')
        finally:
            await file.close()
        image_url = f'uploads/announcement_images/{filename}'
        return image_url

    @staticmethod
    async def broadcast_announcement(session: AsyncSession, bot: Bot, announcement_id: int) -> dict[str, int]:
        users = await UserRepository.get_subscribed_users(session)
        announcement = await AnnouncementRepository.get_announcement_by_id(session, announcement_id)

        if not announcement:
            return {'success': 0, 'failed': len(users)}

        translations_map = {
            tr.language_code: tr.text
            for tr in announcement.languages
        }
        success_count = 0
        failed_count = 0

        for user in users:
            if user.language_code in translations_map:
                user_message = translations_map[user.language_code]
            else:
                user_message = translations_map.get(config.telegram.DEFAULT_LANGUAGE)

            if user_message is None:
                failed_count += 1
                continue

            success = await AdminPanelService.send_message_to_user(
                bot=bot,
                user_id=user.id,
                message=user_message,
                image_url=announcement.image_url
            )
            if success:
                success_count += 1
            else:
                failed_count += 1
        return {'success': success_count, 'failed': failed_count}

    @staticmethod
    async def send_message_to_user(bot: Bot, user_id: int, message: str, image_url: str | None) -> bool:
        try:
            if image_url and Path(image_url).exists():
                image = FSInputFile(image_url)
                await bot.send_photo(
                    chat_id=user_id,
                    photo=image,
                    caption=message
                )
            else:
                await bot.send_message(chat_id=user_id, text=message)
            return True
        except TelegramForbiddenError:
            return False
        except Exception as e:  # noqa
            # logger.error(f'Failed to send message to user {user_id}: {e}')
            return False
