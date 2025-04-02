from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.static_data import STATUS_LIMITS
from bot.common.utils import get_current_date, get_current_time
from core.schemas import RemainingTimeSchema, UserActivitySchema, UserCreateSchema, UserKeyGenerationSchema
from core.schemas.referral import ReferralAddingSchema
from db.repositories import ReferralsRepository, UserRepository


class UserService:

    @staticmethod
    async def user_registration(session: AsyncSession, user_id: int, user: UserCreateSchema) -> bool:
        exists_user: bool = await UserRepository.check_user_exists(session, user_id)
        if exists_user:
            return False

        await UserRepository.add_user(session, user)
        return True

    @staticmethod
    async def referral_adding(session: AsyncSession, referrer_id: int, referred_id: int) -> int | None:
        if not await UserRepository.check_user_exists(session, referrer_id):
            return None

        referrals_data = ReferralAddingSchema(referrer_id=referrer_id, referred_id=referred_id)
        await ReferralsRepository.add_referral(session, referrals_data)
        return referrer_id

    @staticmethod
    async def get_hamster_keys_request_validation(session: AsyncSession, user_id: int) -> UserKeyGenerationSchema:
        user_activity: UserActivitySchema = await UserRepository.get_user_activity_data(session, user_id)
        if user_activity is None:
            # TODO: Implement logging
            # logger.warning(f'User activity data not found for user_id={user_id}')
            return UserKeyGenerationSchema(can_generate=False)

        await UserService._reset_daily_request_if_needed(
            session=session,
            user_id=user_id,
            last_request_datetime=user_activity.last_request_datetime
        )
        return UserService._check_user_daily_limits(user_activity)


    @staticmethod
    async def _reset_daily_request_if_needed(session: AsyncSession, user_id: int, last_request_datetime: datetime):
        if not last_request_datetime:
            return

        current_date = get_current_date()
        if last_request_datetime.date() < current_date:
            try:
                await UserRepository.reset_daily_request(session, user_id)
            except Exception as e:
                print(f'Failed to reset daily request for user_id={user_id}: {e}')
                # TODO: Implement logging
                # logger.error(f'Failed to reset daily request for user_id={user_id}: {e}')

    @staticmethod
    def _check_user_daily_limits(user_activity: UserActivitySchema) -> UserKeyGenerationSchema:
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

        return UserKeyGenerationSchema(can_generate=True)
