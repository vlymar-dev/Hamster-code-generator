import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.user import User
from infrastructure.repositories.referral_repo import ReferralRepository
from tgbot.config import config
from tgbot.exceptions.exceptions import UserAlreadyExistsException

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user: User) -> None:
        try:
            result = await self.session.execute(select(User).where(User.id == user.id))
            existing_user = result.scalar_one_or_none()
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

    async def check_user_exists(self, user_id: int) -> bool:
        try:
            result = await self.session.execute(select(User.id).where(User.id == user_id))
            return result.scalar_one_or_none() is not None
        except DatabaseError as e:
            logger.error(f"Database error occurred while checking user_id={user_id}: {e}")
            return False

    # TODO: Заменить в старт хендлере на check_user_exists
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
            result = await self.session.execute(select(User.language_code).where(User.id == user_id))
            language = result.scalar_one_or_none()
            return language if language else 'en'
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
            result = await self.session.execute(select(User.is_subscribed).where(User.id == user_id))
            is_subscribed = result.scalar_one_or_none()
            return bool(is_subscribed)
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to get subscription status for user_id={user_id}: {e}')
            return True

    async def unsubscribe_notifications(self, user_id: int, referral_repo: ReferralRepository) -> str :
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if user:
                count_referrals = await referral_repo.get_referral_count(user_id)
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

    async def get_user_progress(self, user_id: int, referral_repo: ReferralRepository)-> Optional[dict[str, any]]:
        try:
            result = await self.session.execute(
                select(
                    User.registration_date,
                    User.user_status,
                    User.total_keys_generated
                ).where(User.id == user_id)
            )
            user_data = result.one_or_none()
            if user_data:
                registration_date, user_status, total_keys_generated = user_data
                count_referrals = await referral_repo.get_referral_count(user_id)
                return {
                    'referrals': count_referrals,
                    'registration_date': registration_date,
                    'user_status': user_status,
                    'total_keys_generated': total_keys_generated,
                }
            return None
        except DatabaseError as e:
            logger.error(f"Database error occurred while retrieving progress for user_id={user_id}: {e}")
            return None

    async def get_user_role(self, user_id: int) -> str:
        try:
            result = await self.session.execute(select(User.user_role).where(User.id == user_id))
            user_role = result.scalar_one_or_none()
            return user_role if user_role else 'user'
        except DatabaseError as e:
             logger.error(f"Database error occurred while getting role for user_id={user_id}: {e}")
             return 'user'

    async def change_user_role(self, user_id: int, new_user_role: str) -> str:
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if user:
                if user.user_role != new_user_role:
                    user.user_role = new_user_role
                    await self.session.commit()
                    return 'success'
                return 'unchanged'
            return 'user_not_found'
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f"Database error occurred while changing role for user_id={user_id}: {e}")
            return 'error'

    async def get_users_count(self) -> int:
        try:
            result = await self.session.execute(select(func.count()).select_from(User))
            users_count = result.scalar_one()
            return users_count
        except DatabaseError as e:
            logger.error(f"Database error occurred while counting users: {e}")
            return 0

    async def get_users_with_subscription_info(self) -> list[dict]:
        try:
            result = await self.session.execute(
                select(User.id, User.language_code, User.is_subscribed)
            )
            users = result.fetchall()
            return [
                {"id": row.id, "language_code": row.language_code, "is_subscribed": row.is_subscribed}
                for row in users
            ]
        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching all users data: {e}")
            return []
