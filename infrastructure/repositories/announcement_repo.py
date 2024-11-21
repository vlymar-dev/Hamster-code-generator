import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
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

    async def add_translation_if_exists(self, translation: AnnouncementTranslation) -> AnnouncementTranslation:
        try:
            query = select(Announcement).where(Announcement.id == translation.announcement_id)
            result = await self.session.execute(query)
            announcement = result.scalar_one_or_none()

            if not announcement:
                raise ValueError(f"Announcement with ID {translation.announcement_id} does not exist.")

            self.session.add(translation)
            await self.session.commit()
            return translation
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Translation for this language already exists: {e}")
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_all_announcements_with_languages(self) -> list[dict]:
        try:
            query = (
                select(Announcement.id, Announcement.title, AnnouncementTranslation.language_code)
                .join(AnnouncementTranslation, Announcement.id == AnnouncementTranslation.announcement_id, isouter=True)
            )
            result = await self.session.execute(query)

            announcements = {}
            for row in result.all():
                announcement_id = row.id
                if announcement_id not in announcements:
                    announcements[announcement_id] = {
                        'id': row.id,
                        'title': row.title,
                        'languages': set(),
                    }
                if row.language_code:
                    announcements[announcement_id]['languages'].add(row.language_code)

            for announcement in announcements.values():
                announcement['languages'] = list(announcement['languages'])

            return list(announcements.values())
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching announcements with languages: {e}")
            return []

    async def get_announcement_or_error(self, announcement_id: int) -> Announcement:
        try:
            query = select(Announcement).options(joinedload(Announcement.translations_text)).where(
                Announcement.id == announcement_id)
            result = await self.session.execute(query)
            announcement = result.unique().scalar_one_or_none()

            if not announcement:
                raise ValueError(f"Announcement with ID {announcement_id} does not exist.")

            return announcement
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching announcement ID={announcement_id}: {e}")
            raise

    async def delete_announcement_with_translations(self, announcement_id: int) -> None:
        try:
            query = select(Announcement).where(Announcement.id == announcement_id)
            result = await self.session.execute(query)
            announcement = result.scalar_one_or_none()

            if not announcement:
                raise ValueError(f"Announcement with ID {announcement_id} does not exist.")

            await self.session.delete(announcement)
            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error occurred while deleting announcement ID={announcement_id}: {e}")
            raise

    async def get_translation(self, announcement_id: int, language_code: str) -> Optional[AnnouncementTranslation]:
        try:
            query = (
                select(AnnouncementTranslation)
                .where(
                    AnnouncementTranslation.announcement_id == announcement_id,
                    AnnouncementTranslation.language_code == language_code
                )
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching translation for announcement ID={announcement_id}, "
                         f"language={language_code}: {e}")
            raise

    async def update_translation(self, translation: AnnouncementTranslation) -> AnnouncementTranslation:
        try:
            query = (
                select(AnnouncementTranslation)
                .where(
                    AnnouncementTranslation.announcement_id == translation.announcement_id,
                    AnnouncementTranslation.language_code == translation.language_code
                )
            )
            result = await self.session.execute(query)
            existing_translation = result.scalar_one_or_none()

            if not existing_translation:
                raise ValueError(f'Translation for announcement ID {translation.announcement_id} and language '
                                 f'{translation.language_code} does not exist.')

            existing_translation.text = translation.text
            await self.session.commit()
            return existing_translation
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f'Error when creating or updating a translation: {e}')