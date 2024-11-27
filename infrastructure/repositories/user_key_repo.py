import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.user import User

logger = logging.getLogger(__name__)

class UserKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_user_activity(self, user_id: int, increment_keys: int = 1, increment_requests: int = 1) -> bool:
        """Updates the number of keys, queries, and the time of the last query."""
        try:
            await self.session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    total_keys_generated=User.total_keys_generated + increment_keys,
                    daily_requests_count=User.daily_requests_count + increment_requests,
                    last_request_datetime=datetime.now().replace(second=0, microsecond=0),
                )
            )
            await self.session.commit()
            return True
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error when updating user activity for user_id={user_id}: {e}')
            return False

    async def reset_daily_request(self, user_id: int) -> bool:
        """Reset the count of daily requests to zero."""
        try:
            await self.session.execute(
                update(User).where(User.id == user_id).values(daily_requests_count=0)
            )
            await self.session.commit()
            return True
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error when resetting daily requests for user_id={user_id}: {e}')
            return False

    async def get_daily_requests(self, user_id: int) -> Optional[int]:
        """Get the number of daily user requests."""
        try:
            result = await self.session.execute(
                select(User.daily_requests_count).where(User.id == user_id)
            )
            daily_requests = result.scalar_one_or_none()
            return daily_requests
        except DatabaseError as e:
            logger.error(f'Database error when retrieving daily requests for user_id={user_id}: {e}')
            return None

    async def get_last_request_datetime(self, user_id: int) -> Optional[datetime]:
        """Get the last request datetime of a user."""
        try:
            result = await self.session.execute(
                select(User.last_request_datetime).where(User.id == user_id)
            )
            last_request_datetime = result.scalar_one_or_none()
            return last_request_datetime
        except DatabaseError as e:
            logger.error(f'Database error when retrieving last request time for user_id={user_id}: {e}')
            return None
