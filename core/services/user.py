import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.static_data import STATUS_LIMITS
from bot.common.utils import get_current_date, get_current_time
from core.schemas import RemainingTimeSchema, UserActivitySchema, UserCreateSchema, UserKeyGenerationSchema
from core.schemas.referral import ReferralAddingSchema
from db.repositories import ReferralsRepository, UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service handling user registration, referrals, and key generation validation"""

    @staticmethod
    async def user_registration(session: AsyncSession, user_id: int, user_data: UserCreateSchema) -> bool:
        """Register a new user if not exists"""
        logger.debug(f'Attempting registration for user {user_id}')
        exists_user: bool = await UserRepository.check_user_exists(session, user_id)
        if exists_user:
            logger.debug(f'User {user_id} already exists, skipping registration')
            return False
        try:
            await UserRepository.add_user(session, user_data)
            logger.info(f'Successfully registered new user {user_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to register user {user_id}: {e}', exc_info=True)
            raise

    @staticmethod
    async def referral_adding(session: AsyncSession, referrer_id: int, referred_id: int) -> int | None:
        """Add referral relationship between users"""
        logger.debug(f'Processing referral from {referrer_id} to {referred_id}')
        if not await UserRepository.check_user_exists(session, referrer_id):
            logger.warning(f'Invalid referrer {referrer_id}, user not found')
            return None

        try:
            referrals_data = ReferralAddingSchema(referrer_id=referrer_id, referred_id=referred_id)
            await ReferralsRepository.add_referral(session, referrals_data)
            logger.info(f'Added referral {referrer_id} -> {referred_id}')

            return referrer_id
        except Exception as e:
            logger.error(f'Failed to add referral: {e}', exc_info=True)
            raise

    @staticmethod
    async def get_hamster_keys_request_validation(session: AsyncSession, user_id: int) -> UserKeyGenerationSchema:
        """Validate user's ability to generate hamster keys"""
        logger.debug(f'Validating key generation for user {user_id}')

        user_activity: UserActivitySchema = await UserRepository.get_user_activity_data(session, user_id)
        if user_activity is None:
            logger.warning(f'User activity data not found for user_id={user_id}')
            return UserKeyGenerationSchema(can_generate=False)

        try:
            await UserService._reset_daily_request_if_needed(
                session=session,
                user_id=user_id,
                last_request_datetime=user_activity.last_request_datetime
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
                await UserRepository.reset_daily_request(session, user_id)
            except Exception as e:
                logger.error(f'Daily reset failed for user {user_id}: {e}', exc_info=True)
                raise

    @staticmethod
    def _check_user_daily_limits(user_activity: UserActivitySchema) -> UserKeyGenerationSchema:
        """Check user's daily limits and cooldowns"""
        logger.debug(f"Checking limits for {user_activity.user_id}")

        try:
            daily_limit = STATUS_LIMITS[user_activity.user_status]['daily_limit']
            interval_seconds = STATUS_LIMITS[user_activity.user_status]['interval_minutes'] * 60
            elapsed_seconds = int((get_current_time() - user_activity.last_request_datetime).total_seconds())

            if not user_activity.last_request_datetime:
                return UserKeyGenerationSchema(can_generate=True)

            if user_activity.daily_requests_count >= daily_limit:
                return UserKeyGenerationSchema(daily_limit_exceeded=True)

            if elapsed_seconds < interval_seconds:
                remaining_time = RemainingTimeSchema(
                    minutes=int((interval_seconds - elapsed_seconds) // 60),
                    seconds=int((interval_seconds - elapsed_seconds) % 60)
                )
                return UserKeyGenerationSchema(remaining_time=remaining_time)
            logger.debug("User passed all checks")
            return UserKeyGenerationSchema(can_generate=True)
        except Exception as e:
            logger.error(f'Error checking users daily limits: {e}', exc_info=True)
            raise
