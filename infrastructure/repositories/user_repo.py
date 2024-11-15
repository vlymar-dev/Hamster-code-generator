import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.user_model import User
from tgbot.config import config
from tgbot.exceptions.exceptions import UserAlreadyExistsException

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user: User) -> None:
        try:
            existing_user = await self.session.get(User, user.id)
            if not existing_user:
                self.session.add(user)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f'Integrity error occurred while adding user: {e}')
            raise UserAlreadyExistsException(f"User with id {user.id} already exists.")
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while adding user: {e}')
            raise

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            user = await self.session.get(User, user_id)
            if user:
                return user
            return None
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching user by id {user_id}: {e}")
            return None

    async def get_user_language(self, user_id: int) -> str:
        try:
            user = await self.session.get(User, user_id)
            if user:
                return str(user.language_code)
            return 'en'
        except DatabaseError as e:
            logger.error(f"Database error occurred while getting language for user_id={user_id}: {e}")
            return 'en'

    async def update_user_language(self, user_id: int, selected_language_code: str) -> bool:
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if user:
                if user.language_code != selected_language_code:
                    user.language_code = selected_language_code
                    await self.session.commit()
                return True
            return False
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f"Database error occurred while updating user language for user_id={user_id}: {e}")
            return False

    async def get_subscription_status(self, user_id: int) -> bool:
        try:
            user = await self.session.get(User, user_id)
            if user.is_subscribed:
                return True
            return False
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to get subscription status for user_id={user_id}: {e}')
            return False

    async def unsubscribe_notifications(self, user_id: int) -> str :
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if user:
                count_referrals = await self.session.scalar(
                    select(func.cardinality(User.referrals)).where(User.id == user_id)
                )
                if count_referrals < config.tg_bot.bot_settings.referral_threshold:
                    logger.warning(f'The user with ID {user_id} did not meet the conditions to disable notifications.')
                    return 'conditions_not_met'
                user.is_subscribed = False
                await self.session.commit()
                return 'Unsubscribe successful'
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to unsubscribe for user_id={user_id}: {e}')
            return 'error'

    async def subscribe_notifications(self, user_id: int) -> str :
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_subscribed = True
                await self.session.commit()
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to subscribe for user_id={user_id}: {e}')
            return 'error'