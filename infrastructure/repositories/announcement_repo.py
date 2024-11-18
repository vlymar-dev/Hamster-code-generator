import logging
from cgitb import reset
from typing import Optional

from sqlalchemy import select, exists
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from infrastructure.models.announcement_model import Announcement, AnnouncementTranslation

logger = logging.getLogger(__name__)

class AnnouncementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_announcement(self, announcement: Announcement) -> None:
        try:
            self.session.add(announcement)
            await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while adding announcement: {e}')
            raise

    async def add_translation(self, translation_text: AnnouncementTranslation) -> None:
        try:
            self.session.add(translation_text)
            await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while adding translation: {e}')
            raise

    async def get_all_announcements(self) -> list[Announcement]:
        try:
            query = select(Announcement)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching all announcements: {e}")
            return []

    async def get_announcement_with_translations(self, announcement_id: int) -> Optional[Announcement]:
        try:
            result = await self.session.execute(
                select(Announcement)
                .options(joinedload(Announcement.translations_text))
                .where(Announcement.id == announcement_id)
            )
            return result.unique().scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching announcement with translations: {e}")
            raise

    async def check_announcement_exists(self, announcement_id: int) -> bool:
        try:
            query = select(exists().where(Announcement.id == announcement_id))
            result = await self.session.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error while checking if announcement_id={announcement_id} exists: {e}")
            return False