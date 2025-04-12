import logging
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

logger = logging.getLogger(__name__)


class AdminPanelService:
    """Service handling administrative operations for announcements and broadcasts"""

    @staticmethod
    async def process_and_save_image(photo: PhotoSize, bot: Bot) -> str:
        """Processes and saves an image in WEBP format."""
        filename = f'{uuid.uuid4()}.webp'
        image_dir = BASE_DIR / 'uploads' / 'announcement_images'
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / filename
        logger.debug(f'Processing image: {filename}')

        try:
            file = await bot.download(photo.file_id)
            file.seek(0)

            with Image.open(file) as image:
                if image.mode not in ('RGB', 'RGBA'):
                    logger.info(f'Converting image from {image.mode} to RGB')
                    image = image.convert('RGB')

                output_io = BytesIO()
                image.save(output_io, format='WEBP', quality=85, optimize=True)
                output_io.seek(0)

                async with aiofiles.open(image_path, 'wb') as file:
                    await file.write(output_io.getvalue())
                logger.info(f'Image saved: {image_path}')
        except UnidentifiedImageError:
            raise ValueError('The provided file is not a supported image.')
        except Exception as e:
            logger.error(f'Image processing error: {e}', exc_info=True)
            raise
        finally:
            await file.close()
        image_url = f'uploads/announcement_images/{filename}'
        return image_url

    @staticmethod
    async def broadcast_announcement(session: AsyncSession, bot: Bot, announcement_id: int) -> dict[str, int]:
        """Broadcasts an announcement to all subscribed users"""
        logger.info(f'Initiating broadcast for announcement #{announcement_id}')
        users = await UserRepository.get_subscribed_users(session)
        announcement = await AnnouncementRepository.get_announcement_by_id(session, announcement_id)

        if not announcement:
            logger.error(f'Announcement #{announcement_id} not found')
            return {'success': 0, 'failed': len(users)}

        logger.debug(f'Loaded {len(users)} subscribed users')

        # Create translation map
        translations_map = {
            tr.language_code: tr.text
            for tr in announcement.languages
        }
        success_count = 0
        failed_count = 0

        for user in users:
            try:
                if user.language_code in translations_map:
                    user_message = translations_map[user.language_code]
                    logger.debug(f'Using {user.language_code} translation for user #{user.id}')
                else:
                    logger.warning(f'No translation for {user.language_code}, using default')
                    user_message = translations_map.get(config.telegram.DEFAULT_LANGUAGE)

                if user_message is None:
                    logger.error('No valid translation available')
                    failed_count += 1
                    continue

                # Attempt message delivery
                delivery_status = await AdminPanelService.send_message_to_user(
                    bot=bot,
                    user_id=user.id,
                    message=user_message,
                    image_url=announcement.image_url
                )
                if delivery_status:
                    success_count += 1
                    logger.debug(f'Message delivered to user #{user.id}')
                else:
                    failed_count += 1
                    logger.warning(f'Failed delivery to user #{user.id}')
            except Exception as e:
                logger.error(f'Error sending to user #{user.id}: {e}', exc_info=True)
                failed_count += 1
        logger.info(f'Broadcast complete | Success: {success_count}, Failed: {failed_count}')
        return {'success': success_count, 'failed': failed_count}

    @staticmethod
    async def send_message_to_user(bot: Bot, user_id: int, message: str, image_url: str | None) -> bool:
        """Sends a message to a user with optional image attachment"""
        try:
            logger.debug(f'Sending message to user #{user_id}')
            if image_url and Path(image_url).exists():
                logger.debug(f'Attaching image: {image_url}')
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
            logger.warning(f'User #{user_id} blocked the bot')
            return False
        except Exception as e:
            logger.error(f'Delivery failed to user #{user_id}: {e}', exc_info=True)
            return False
