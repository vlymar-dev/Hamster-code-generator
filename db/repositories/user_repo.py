import logging
from datetime import date

from sqlalchemy import Date, cast, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.shemas import UserCreateSchema, UserProgresSchema
from infrastructure.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:

    @staticmethod
    async def add_user(session: AsyncSession, user: UserCreateSchema) -> None:
        try:
            new_instance = User(**user.model_dump())
            session.add(new_instance)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'Integrity error occurred while adding user: {e}')
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding user: {e}')
            raise

    @staticmethod
    async def check_user_exists(session: AsyncSession, user_id: int) -> bool:
        return await session.get(User, user_id) is not None

    @staticmethod
    async def get_user_language(session: AsyncSession, user_id: int) -> str:
        try:
            result = await session.execute(select(User.language_code).where(User.id == user_id))
            language = result.scalar_one_or_none()
            return language if language else 'en'
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while getting language for user_id={user_id}: {e}')
            return 'en'

    @staticmethod
    async def is_user_banned(session: AsyncSession, user_id: int) -> bool:
        try:
            result = await session.execute(select(User.is_banned).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
             logger.error(f'Database error occurred while checking ban status for user_id={user_id}: {e}')
             return True

    @staticmethod
    async def get_subscription_status(session: AsyncSession, user_id: int) -> bool:
        try:
            result = await session.execute(select(User.is_subscribed).where(User.id == user_id))
            is_subscribed = result.scalar_one_or_none()
            return is_subscribed
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while trying to get subscription status for user_id={user_id}: {e}')
            return True

    @staticmethod
    async def get_user_role(session: AsyncSession, user_id: int) -> str:
        try:
            result = await session.execute(select(User.user_role).where(User.id == user_id))
            user_role = result.scalar_one_or_none()
            return user_role if user_role else 'user'
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while getting role for user_id={user_id}: {e}')
            return 'user'

    @staticmethod
    async def update_user_language(session: AsyncSession, user_id: int, selected_language_code: str) -> bool:
        try:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(language_code=selected_language_code)
            )
            if result.rowcount:
                await session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while updating user language for user_id={user_id}: {e}')
            return False

    @staticmethod
    async def update_subscription_status(session: AsyncSession, user_id: int, is_subscribed: bool) -> None:
        try:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_subscribed=is_subscribed)
            )
            if result.rowcount:
                await session.commit()
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while trying to update_subscription_status for user_id={user_id}: {e}')

    @staticmethod
    async def get_user_progress(session: AsyncSession, user_id: int)-> UserProgresSchema | None:
        try:
            result = await session.execute(
                select(
                    User.registration_date,
                    User.user_status,
                    User.total_keys_generated
                ).where(User.id == user_id)
            )
            row = result.one_or_none()
            if not row:
                return None

            return UserProgresSchema(
                registration_date=row.registration_date,
                user_status=row.user_status,
                total_keys_generated=row.total_keys_generated
            )
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while retrieving progress for user_id={user_id}: {e}')
            return None

    @staticmethod
    async def get_today_keys_count(session: AsyncSession) -> int:
        try:
            today = date.today()
            result = await session.execute(
                select(func.sum(User.daily_requests_count))
                .where(cast(User.last_request_datetime, Date) == today)
            )
            today_keys = result.scalar_one_or_none()
            return today_keys if today_keys else 0
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while calculating total keys: {e}')
            return 0
