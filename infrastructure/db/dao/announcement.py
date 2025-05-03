import logging
from collections import defaultdict

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from infrastructure.db.dao.base import BaseDAO
from infrastructure.db.models import Announcement, AnnouncementTranslation
from infrastructure.schemas import AnnouncementTranslationSchema, AnnouncementWithLanguagesSchema

logger = logging.getLogger(__name__)


class AnnouncementTranslationDAO(BaseDAO[AnnouncementTranslation]):
    """DAO for announcement translation code management."""

    model = AnnouncementTranslation

    @classmethod
    async def find_by_announcement_and_language(
        cls, session: AsyncSession, announcement_id: int, language_code: str
    ) -> BaseModel | None:
        """Retrieves specific translation for announcement and language.

        Args:
            session (AsyncSession): The database session.
            announcement_id (int): ID of the related announcement.
            language_code (str): Language code of the translation.

        Returns:
            BaseModel | None: Translation data if found, None otherwise.
            Returns None on error.
        """
        logger.info(f'Fetching translation for announcement ID {announcement_id}, language {language_code}')

        try:
            result = await session.execute(
                select(cls.model).where(
                    cls.model.announcement_id == announcement_id, cls.model.language_code == language_code
                )
            )
            translation = result.scalar_one_or_none()

            if not translation:
                logger.debug(f'Translation not found for announcement ID {announcement_id}, language {language_code}')
                return None

            return AnnouncementTranslationSchema(
                id=translation.id, language_code=translation.language_code, text=translation.text
            )

        except SQLAlchemyError as e:
            logger.error(
                f'Database error fetching translation for announcement ID={announcement_id}, '
                f'language={language_code}: {e}'
            )
            return None


class AnnouncementDAO(BaseDAO[Announcement]):
    """DAO for announcement code management."""

    model = Announcement

    @classmethod
    async def find_all_with_languages(cls, session: AsyncSession, limit: int = 20) -> list[BaseModel]:
        """Retrieves all announcements with their available languages.

        Args:
            session (AsyncSession): The database session.
            limit (int): Maximum number of announcements to return. Defaults to 20.

        Returns:
            list[BaseModel]: list of announcements with language info.
            Returns empty list on error.
        """
        logger.info(f'Fetching up to {limit} announcements with language info')

        try:
            query = (
                select(Announcement.id, Announcement.title, AnnouncementTranslation.language_code)
                .select_from(Announcement)
                .outerjoin(AnnouncementTranslation, Announcement.id == AnnouncementTranslation.announcement_id)
                .order_by(Announcement.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(query)

            # Group results by announcement ID
            grouped = defaultdict(lambda: {'title': None, 'languages': set()})
            for announcement_id, title, lang in result.all():
                grouped[announcement_id]['title'] = title
                if lang:
                    grouped[announcement_id]['languages'].add(lang)

            return [
                AnnouncementWithLanguagesSchema(
                    id=announcement_id,
                    title=data['title'],
                    languages=[AnnouncementTranslationSchema(language_code=lang) for lang in sorted(data['languages'])],
                )
                for announcement_id, data in grouped.items()
            ]

        except SQLAlchemyError as e:
            logger.error(f'Database error fetching announcements with languages: {e}')
            return []

    @classmethod
    async def find_by_id_with_languages(cls, session: AsyncSession, announcement_id: int) -> BaseModel | None:
        """Retrieves a single announcement with its translations by ID.

        Args:
            session (AsyncSession): The database session.
            announcement_id (int): ID of the announcement to retrieve.

        Returns:
            BaseModel | None: Filled schema if found, None otherwise.
            Returns None on error.
        """
        logger.info(f'Fetching announcement with ID {announcement_id} and its translations')

        try:
            result = await session.execute(
                select(cls.model)
                .options(joinedload(Announcement.translations_text))
                .where(cls.model.id == announcement_id)
            )
            announcement = result.unique().scalar_one_or_none()

            if not announcement:
                logger.debug(f'Announcement with ID {announcement_id} not found')
                return None

            languages = [
                AnnouncementTranslationSchema(language_code=translation.language_code, text=translation.text)
                for translation in announcement.translations_text
            ]

            return AnnouncementWithLanguagesSchema(
                id=announcement.id, title=announcement.title, image_url=announcement.image_url, languages=languages
            )

        except SQLAlchemyError as e:
            logger.error(f'Database error fetching announcement ID={announcement_id}: {e}')
            return None
