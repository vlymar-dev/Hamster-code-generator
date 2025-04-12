import logging
from collections import defaultdict

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from infrastructure.db.models import Announcement, AnnouncementTranslation
from infrastructure.schemas import (
    AnnouncementCreateSchema,
    AnnouncementTranslationCreateSchema,
    AnnouncementTranslationSchema,
    AnnouncementWithLanguagesSchema,
)

logger = logging.getLogger(__name__)


class AnnouncementRepository:

    @staticmethod
    async def add_announcement(session: AsyncSession, data: AnnouncementCreateSchema) -> None:
        try:
            session.add(Announcement(**data.model_dump()))
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding announcement: {e}')

    @staticmethod
    async def add_translation_by_announcement_id(
            session: AsyncSession,
            translation: AnnouncementTranslationCreateSchema
    ) -> None:
        try:
            session.add(AnnouncementTranslation(**translation.model_dump()))
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding announcement translation: {e}')

    @staticmethod
    async def get_announcement_by_id(
            session: AsyncSession,
            announcement_id: int
    ) -> AnnouncementWithLanguagesSchema | None:
        try:
            result = await session.execute(
                (select(Announcement)
                 .options(joinedload(Announcement.translations_text))
                 .where(Announcement.id == announcement_id))
            )
            announcement = result.unique().scalar_one_or_none()
            if announcement:
                languages = [
                    AnnouncementTranslationSchema(
                        language_code=translation.language_code,
                        text=translation.text
                    )
                    for translation in announcement.translations_text
                ]
                return AnnouncementWithLanguagesSchema(
                    id=announcement.id,
                    title=announcement.title,
                    image_url=announcement.image_url,
                    languages=languages
                )
            return None
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching announcement ID={announcement_id}: {e}')
            return None

    @staticmethod
    async def get_all_announcements_with_languages(
            session: AsyncSession,
            limit: int = 20
    ) -> list[AnnouncementWithLanguagesSchema]:
        try:
            query = (
                select(Announcement.id, Announcement.title, AnnouncementTranslation.language_code)
                .outerjoin(AnnouncementTranslation, Announcement.id == AnnouncementTranslation.announcement_id)
                .order_by(Announcement.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(query)

            grouped = defaultdict(lambda: {'title': None, 'languages': set()})

            for announcement_id, title, lang in result.all():
                grouped[announcement_id]['title'] = title
                if lang:
                    grouped[announcement_id]['languages'].add(lang)

            return [
                AnnouncementWithLanguagesSchema(
                    id=announcement_id,
                    title=data['title'],
                    languages=[
                        AnnouncementTranslationSchema(language_code=lang)
                        for lang in sorted(data['languages'])
                    ]
                )
                for announcement_id, data in grouped.items()
            ]
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching announcements with languages: {e}')
            return []

    @staticmethod
    async def get_translation_by_language_code(
            session: AsyncSession,
            announcement_id: int,
            language_code: str
    ) -> AnnouncementTranslationSchema:
        try:
            result = await session.execute(
                select(AnnouncementTranslation)
                .where(
                    AnnouncementTranslation.announcement_id == announcement_id,
                    AnnouncementTranslation.language_code == language_code
                )
            )
            announcement_translation = result.scalar_one_or_none()
            return AnnouncementTranslationSchema(
                text=announcement_translation.text
            )
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching translation for announcement ID={announcement_id}, '
                         f'language={language_code}: {e}')

    @staticmethod
    async def update_translation(session: AsyncSession, translation: AnnouncementTranslationCreateSchema) -> None:
        try:
            await session.execute(
                update(AnnouncementTranslation)
                .where(AnnouncementTranslation.announcement_id == translation.announcement_id,
                       AnnouncementTranslation.language_code == translation.language_code)
                .values(text=translation.text)
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while updating translation for announcement '
                         f'ID={translation.announcement_id}, language={translation.language_code}: {e}')

    @staticmethod
    async def delete_announcement_by_id(session: AsyncSession, announcement_id: int) -> None:
        try:
            announcement = await session.get(Announcement, announcement_id)
            if announcement:
                await session.delete(announcement)
                await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Error occurred while deleting announcement ID={announcement_id}: {e}')
            return None
