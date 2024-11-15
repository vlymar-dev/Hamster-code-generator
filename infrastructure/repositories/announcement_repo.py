import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class SQLAlchemyAnnouncementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session