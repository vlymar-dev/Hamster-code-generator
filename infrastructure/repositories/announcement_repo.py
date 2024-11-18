import logging

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

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

    # async def get_announcement_by_id(self, user_id: int) -> Optional[Announcement]:
    #     try:
    #         announcement = await self.session.get(Announcement, user_id)
    #         if announcement:
    #             return announcement
    #         return None
    #     except DatabaseError as e:
    #         logger.error(f"Database error occurred while fetching announcement by id {user_id}: {e}")
    #         return None