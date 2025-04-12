import logging
from datetime import date, datetime

from sqlalchemy import Date, cast, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import SubscribedUsersSchema, UserActivitySchema, UserCreateSchema, UserProgressSchema
from db.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:

    @staticmethod
    async def add_user(session: AsyncSession, user_data: UserCreateSchema) -> None:
        try:
            new_instance = User(**user_data.model_dump())
            session.add(new_instance)
            await session.flush()
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
        try:
            return await session.get(User, user_id) is not None
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while checking user exists: {e}')
            raise

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
    async def get_user_role(session: AsyncSession, target_user_id: int) -> str | None:
        try:
            result = await session.execute(select(User.user_role).where(User.id == target_user_id))
            user_role = result.scalar_one_or_none()
            return user_role if user_role else None
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while getting role for user_id={target_user_id}: {e}')
            return None

    @staticmethod
    async def update_user_role(session: AsyncSession, user_id: int, new_user_role: str) -> None:
        try:
            await session.execute(
                update(User).where(User.id == user_id).values(user_role=new_user_role)
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while changing role for user_id={user_id}: {e}')
            return None

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
            logger.error(f'Database error occurred while trying to update_subscription for user_id={user_id}: {e}')

    @staticmethod
    async def get_user_progress(session: AsyncSession, user_id: int) -> UserProgressSchema | None:
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

            return UserProgressSchema(
                registration_date=row.registration_date,
                user_status=row.user_status,
                total_keys_generated=row.total_keys_generated
            )
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while retrieving progress for user_id={user_id}: {e}')
            return None

    @staticmethod
    async def get_user_activity_data(session: AsyncSession, user_id: int) -> UserActivitySchema | None:
        """Gets daily requests, time of last request, and user status per request."""
        try:
            result = await session.execute(
                select(
                    User.daily_requests_count,
                    User.last_request_datetime,
                    User.user_status
                ).where(User.id == user_id)
            )
            row = result.one_or_none()
            if not row:
                return None

            return UserActivitySchema(
                daily_requests_count=row.daily_requests_count,
                last_request_datetime=row.last_request_datetime,
                user_status=row.user_status
            )
        except SQLAlchemyError as e:
            logger.error(f'Database error when retrieving user activity data for user_id={user_id}: {e}')
            return None

    @staticmethod
    async def update_user_activity(
            session: AsyncSession,
            user_id: int,
            increment_keys: int = 1,
            increment_requests: int = 1
    ) -> None:
        """Updates the number of keys, queries, and the time of the last query."""
        try:
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    total_keys_generated=User.total_keys_generated + increment_keys,
                    daily_requests_count=User.daily_requests_count + increment_requests,
                    last_request_datetime=datetime.now(),
                )
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error when updating user activity for user_id={user_id}: {e}')

    @staticmethod
    async def reset_daily_request(session: AsyncSession, user_id: int) -> None:
        """Reset the count of daily requests to zero."""
        try:
            await session.execute(
                update(User).where(User.id == user_id).values(daily_requests_count=0)
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error when resetting daily requests for user_id={user_id}: {e}')

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

    @staticmethod
    async def get_users_count(session: AsyncSession) -> int:
        try:
            result = await session.execute(select(func.count()).select_from(User).select_from(User))
            return result.scalar_one()
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while counting users: {e}')
            return 0

    @staticmethod
    async def get_subscribed_users(session: AsyncSession) -> list[SubscribedUsersSchema]:
        try:
            result = await session.execute(
                select(User)
                .where(User.is_subscribed)
            )
            users = result.scalars().all()
            return [SubscribedUsersSchema.model_validate(user) for user in users]
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while fetching all users data: {e}')
            return []
