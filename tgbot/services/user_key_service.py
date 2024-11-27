import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.sql.functions import current_time

from infrastructure.repositories.user_key_repo import UserKeyRepository
from tgbot.common.staticdata import STATUS_LIMITS
from tgbot.common.utils import format_seconds_to_minutes_and_seconds, get_current_time

logger = logging.getLogger(__name__)


class UserKeyService:

    @staticmethod
    async def update_user_activity(user_id: int, user_key_repo: UserKeyRepository) -> bool:
        """Updates all the user's activity settings."""
        try:
            return await user_key_repo.update_user_activity(user_id)
        except Exception as e:
            logger.error(f'Error when updating user activity for user_id={user_id}: {e}')
            return False

    @staticmethod
    async def validate_user_request(user_id: int, user_key_repo: UserKeyRepository) -> dict:
        """Check all conditions for key generation."""
        try:
            daily_requests, last_request, user_status = await UserKeyService._get_user_data(user_id, user_key_repo)

            if not UserKeyService._check_daily_limit(daily_requests, user_status):
                return {'can_generate': False, 'reason': 'daily_limit_exceeded', 'remaining_time': None}

            remaining_time = UserKeyService._check_request_interval(last_request, user_status)
            if remaining_time is not None:
                print(remaining_time)
                return {'can_generate': False, 'reason': 'interval_not_met', 'remaining_time': remaining_time}

            return {'can_generate': True, 'reason': None, 'remaining_time': None}

        except Exception as e:
            logger.error(f'Error when checking key generation conditions for user_id={user_id}: {e}')
            return {'can_generate': False, 'reason': 'error', 'remaining_time': None}

    @staticmethod
    async def _get_user_data(user_id: int, user_key_repo: UserKeyRepository) -> tuple:
        """Retrieves user data in a single query."""
        user_data = await user_key_repo.get_user_activity_data(user_id)
        if not user_data:
            raise ValueError("User data not found")
        return user_data['daily_requests_count'], user_data['last_request_datetime'], user_data['user_status']

    @staticmethod
    def _check_daily_limit(today_keys: int, user_status: str) -> bool:
        """Check the daily key limit has not been reached."""
        daily_limit = STATUS_LIMITS[user_status]['daily_limit']
        return today_keys < daily_limit

    @staticmethod
    def _check_request_interval(last_request: Optional[datetime], user_status: str) -> Optional[dict]:
        if not last_request:
            return None
        interval_seconds = STATUS_LIMITS[user_status]['interval_minutes'] * 60
        elapsed_seconds = int((get_current_time() - last_request).total_seconds())

        if elapsed_seconds < interval_seconds:
            return format_seconds_to_minutes_and_seconds(interval_seconds - elapsed_seconds)
        return None
