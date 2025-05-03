import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao import ReferralDAO, UserDAO
from infrastructure.db.models import User
from infrastructure.schemas import (
    RemainingTimeSchema,
    UserActivitySchema,
    UserAuthSchema,
    UserCreateSchema,
    UserDailyRequestsSchema,
    UserKeyGenerationSchema,
    UserLanguageCodeSchema,
    UserRoleSchema,
)
from infrastructure.schemas.referral import ReferralAddingSchema
from infrastructure.services import CacheService
from infrastructure.services.cache import CacheKeys
from infrastructure.utils import STATUS_LIMITS, get_current_date, get_current_time

logger = logging.getLogger(__name__)


class UserCacheService:
    """User data caching operations."""

    @staticmethod
    async def get_user_language(
        cache_service: CacheService, session: AsyncSession, user_id: int
    ) -> UserLanguageCodeSchema:
        """Get user language from cache or database."""
        logger.debug(f'Getting language for user {user_id}')
        return await cache_service.get_or_set(
            key=CacheKeys.LANGUAGE.format(user_id=user_id),
            model=UserLanguageCodeSchema,
            fetch_func=UserService.get_user_language,
            session=session,
            user_id=user_id,
        )

    @staticmethod
    async def update_user_language(
        cache_service: CacheService, session: AsyncSession, user_id: int, selected_language_code: str
    ) -> UserLanguageCodeSchema:
        """Update user language in both cache and database."""
        logger.debug(f'Updating language for user {user_id} to {selected_language_code}')
        return await cache_service.refresh(
            key=CacheKeys.LANGUAGE.format(user_id=user_id),
            fetch_func=UserService.update_user_language,
            session=session,
            user_id=user_id,
            selected_language_code=selected_language_code,
        )

    @staticmethod
    async def get_user_auth_data(cache_service: CacheService, session: AsyncSession, user_id: int):
        """Get cached auth data (roles, permissions)."""
        return await cache_service.get_or_set(
            key=CacheKeys.USER_DATA.format(user_id=user_id),
            model=UserAuthSchema,
            fetch_func=UserService.get_user_auth,
            session=session,
            user_id=user_id,
        )

    @staticmethod
    async def update_user_auth_data(
        cache_service: CacheService, session: AsyncSession, user_id: int, new_user_role: str
    ):
        """Update user auth data in cache and DB."""
        return await cache_service.refresh(
            key=CacheKeys.USER_DATA.format(user_id=user_id),
            fetch_func=UserService.update_user_auth,
            session=session,
            user_id=user_id,
            new_user_role=new_user_role,
        )


class UserService:
    """Service handling user registration, referrals, and key generation validation"""

    @staticmethod
    async def user_registration(session: AsyncSession, user_id: int, user_data: UserCreateSchema) -> bool:
        """Register a new user if not exists"""
        logger.debug(f'Attempting registration for user {user_id}')
        if await UserDAO.check_user_exists(session, user_id):
            logger.debug(f'User {user_id} already exists, skipping registration')
            return False
        try:
            await UserDAO.add(session=session, values=user_data)
            logger.info(f'Successfully registered new user {user_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to register user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def referral_adding(session: AsyncSession, referrer_id: int, referred_id: int) -> int | None:
        """Add referral relationship between users"""
        logger.debug(f'Processing referral from {referrer_id} to {referred_id}')
        if not await UserDAO.check_user_exists(session=session, user_id=referrer_id):
            logger.warning(f'Invalid referrer {referrer_id}, user not found')
            return None

        try:
            await ReferralDAO.add(
                session=session, values=ReferralAddingSchema(referrer_id=referrer_id, referred_id=referred_id)
            )
            logger.info(f'Added referral {referrer_id} -> {referred_id}')

            return referrer_id
        except Exception as e:
            logger.error(f'Failed to add referral: {e}', exc_info=True)
            raise

    @staticmethod
    async def get_user_language(session: AsyncSession, user_id: int) -> UserLanguageCodeSchema | None:
        """Get user language code from DB by user_id"""
        logger.debug(f'Fetching language for user {user_id} from DB')
        try:
            language_code = await UserDAO.find_field_by_id(session=session, data_id=user_id, field='language_code')
            return UserLanguageCodeSchema(language_code=language_code)
        except Exception as e:
            logger.error(f'Failed to get language for user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def update_user_language(
        session: AsyncSession, user_id: int, selected_language_code: str
    ) -> UserLanguageCodeSchema:
        """Update user's language code in the DB"""
        logger.debug(f'Updating language for user {user_id} to {selected_language_code}')
        try:
            if await UserDAO.update(
                session=session, data_id=user_id, values=UserLanguageCodeSchema(language_code=selected_language_code)
            ):
                logger.info(f'Updated language for user {user_id}')
                return UserLanguageCodeSchema(language_code=selected_language_code)
        except Exception as e:
            logger.error(f'Failed to update language for user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def get_user_auth(session: AsyncSession, user_id: int) -> UserAuthSchema:
        """Fetch user's authorization data from DB"""
        logger.debug(f'Fetching auth data for user {user_id}')
        try:
            user_data: User = await UserDAO.find_one_or_none_by_id(session=session, data_id=user_id)
            return UserAuthSchema(is_banned=user_data.is_banned, user_role=user_data.user_role)
        except Exception as e:
            logger.error(f'Failed to fetch auth data for user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def update_user_auth(session: AsyncSession, user_id: int, new_user_role: str) -> UserAuthSchema:
        """Update user's role in DB and return updated auth data"""
        logger.debug(f'Updating auth data for user {user_id} to role {new_user_role}')
        try:
            await UserDAO.update(session=session, data_id=user_id, values=UserRoleSchema(user_role=new_user_role))
            user_data: User = await UserDAO.find_one_or_none_by_id(session=session, data_id=user_id)
            logger.info(f'Updated role for user {user_id}')
            return UserAuthSchema(is_banned=user_data.is_banned, user_role=user_data.user_role)
        except Exception as e:
            logger.error(f'Failed to update auth data for user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def get_user_keys_request_data(session: AsyncSession, user_id: int) -> UserActivitySchema | None:
        """Fetch user's key generation activity data from the DB."""
        logger.debug(f'Fetching key request data for user {user_id}')
        try:
            user_data: User = await UserDAO.find_one_or_none_by_id(session=session, data_id=user_id)
            if not user_data:
                logger.warning(f'User {user_id} not found in DB')
                return None
            return UserActivitySchema(
                total_keys_generated=user_data.total_keys_generated,
                daily_requests_count=user_data.daily_requests_count,
                last_request_datetime=user_data.last_request_datetime,
                user_status=user_data.user_status,
            )
        except Exception as e:
            logger.error(f'Failed to get key request data for user {user_id}: {e}', exc_info=True)
            return None

    @staticmethod
    async def get_hamster_keys_request_validation(
        session: AsyncSession, user_activity: UserActivitySchema, user_id: int
    ) -> UserKeyGenerationSchema:
        """Validate user's ability to generate hamster keys"""
        logger.debug(f'Validating key generation for user {user_id}')

        if user_activity is None:
            logger.warning(f'User activity data not found for user_id={user_id}')
            return UserKeyGenerationSchema(can_generate=False)

        try:
            await UserService._reset_daily_request_if_needed(
                session=session, user_id=user_id, last_request_datetime=user_activity.last_request_datetime
            )
            return UserService._check_user_daily_limits(user_activity)
        except Exception as e:
            logger.error(f'Validation failed for user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def _reset_daily_request_if_needed(session: AsyncSession, user_id: int, last_request_datetime: datetime):
        """Reset daily request counter if date changed"""
        if not last_request_datetime:
            logger.debug(f'No previous requests for user {user_id}')
            return

        current_date = get_current_date()
        if last_request_datetime.date() < current_date:
            logger.info(f'Resetting daily counter for user {user_id}')
            try:
                await UserDAO.update(
                    session=session, data_id=user_id, values=UserDailyRequestsSchema(daily_requests_count=0)
                )
            except Exception as e:
                logger.error(f'Daily reset failed for user {user_id}: {e}', exc_info=True)
                raise

    @staticmethod
    def _check_user_daily_limits(user_activity: UserActivitySchema) -> UserKeyGenerationSchema:
        """Check user's daily limits and cooldowns"""
        logger.debug('Checking limits')

        try:
            daily_limit = STATUS_LIMITS[user_activity.user_status]['daily_limit']
            if not user_activity.last_request_datetime:
                return UserKeyGenerationSchema(can_generate=True)

            if user_activity.daily_requests_count >= daily_limit:
                return UserKeyGenerationSchema(daily_limit_exceeded=True)

            interval_seconds = STATUS_LIMITS[user_activity.user_status]['interval_minutes'] * 60
            elapsed_seconds = int((get_current_time() - user_activity.last_request_datetime).total_seconds())

            if elapsed_seconds < interval_seconds:
                remaining_time = RemainingTimeSchema(
                    minutes=int((interval_seconds - elapsed_seconds) // 60),
                    seconds=int((interval_seconds - elapsed_seconds) % 60),
                )
                return UserKeyGenerationSchema(remaining_time=remaining_time)
            logger.debug('User passed all checks')
            return UserKeyGenerationSchema(can_generate=True)
        except Exception as e:
            logger.error(f'Error checking users daily limits: {e}', exc_info=True)
            raise
