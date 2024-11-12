import logging
from typing import Any, Optional

from sqlalchemy import select
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
                print(f'Пользователь с ID {user_id} использует свою же реферальную ссылку.')  # noqa
                raise SelfReferralException()

            existing_user = await self.session.get(User, user_id)
            if existing_user:
                print(f'Пользователь с ID {user_id} уже существует.')   # noqa
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

