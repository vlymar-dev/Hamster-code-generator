import logging
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.database.models import User
from tgbot.exceptions.exceptions import SelfReferralException, UserAlreadyExistsException

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user_data: dict[str, Any]) -> None:
        try:
            user = await self.session.get(User, user_data["id"])
            if not user:
                user = User(**user_data)
                self.session.add(user)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f'Integrity error occurred while adding user: {e}')
            raise
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f'Database error occurred while adding user: {e}')
            raise

    async def get_user_language(self, user_id: int) -> str:
        try:
            user = await self.session.get(User, user_id)
            if user:
                return str(user.language_code)
            return 'en'
        except DatabaseError as e:
            logger.error(f"Database error occurred while getting language for user_id={user_id}: {e}")
            return 'en'

    async def update_user_language(self, user_id: int, selected_language_code: str) -> None:
        try:
            user = await self.session.get(User, user_id)
            if user:
                if user.language_code != selected_language_code:
                    user.language_code = selected_language_code
                    await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f"Database error occurred while updating user language for user_id={user_id}: {e}")
            raise

    async def add_referral(self, user_id: int, referral_id: int):
        try:
            if user_id == referral_id:
                logger.warning(f'The user with ID {user_id} uses their own referral link.')
                raise SelfReferralException()

            existing_user = await self.session.get(User, user_id)
            if existing_user:
                logger.warning(f'The user with ID {user_id} already exists.')
                raise UserAlreadyExistsException()

            referrer_user = await self.session.get(User, referral_id)
            if referrer_user:
                referrer_user.referrals = referrer_user.referrals + [user_id]
                await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f"Database error occurred while adding referral for user_id={user_id}, referral_id={referral_id}: {e}")
            raise

    async def get_user_progress(self, user_id: int)-> Optional[dict[str, any]]:
        try:
            result = await self.session.execute(
                select(
                    User.referrals,
                    User.registration_date,
                    User.user_status,
                    User.total_keys_generated
                ).where(User.id == user_id)
            )
            user_data = result.one_or_none()
            if user_data:
                referrals, registration_date, user_status, total_keys_generated = user_data
                return {
                    'referrals': len(referrals) if referrals else 0,
                    'registration_date': registration_date,
                    'user_status': user_status,
                    'total_keys_generated': total_keys_generated,
                }
            return None
        except DatabaseError as e:
            logger.error(f"Database error occurred while retrieving progress for user_id={user_id}: {e}")
            return None

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
            user = await self.session.get(User, user_id)
            if user:
                count_referrals = await self.session.scalar(
                    select(func.cardinality(User.referrals)).where(User.id == user_id)
                )
                if count_referrals < 10:
                    logger.warning(f'The user with ID {user_id} uses their own referral link.')
                    return 'conditions_not_met'
                user.is_subscribed = False
                await self.session.commit()
                return 'Unsubscribe successful'
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to unsubscribe for user_id={user_id}: {e}')
            return 'error'

    async def subscribe_notifications(self, user_id: int) -> str :
        try:
            user = await self.session.get(User, user_id)
            if user:
                user.is_subscribed = True
                await self.session.commit()
        except DatabaseError as e:
            logger.error(f'Database error occurred while trying to subscribe for user_id={user_id}: {e}')
            return 'error'