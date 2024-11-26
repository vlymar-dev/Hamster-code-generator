import logging
from typing import Optional

from infrastructure.repositories.user_key_repo import UserKeyRepository
from tgbot.common.staticdata import STATUS_LIMITS
from tgbot.common.utils import format_seconds_to_minutes_and_seconds, get_current_time

logger = logging.getLogger(__name__)


class UserKeyService:

    @staticmethod
    async def increment_keys(user_id: int, user_key_repo: UserKeyRepository) -> bool:
        try:
            return await user_key_repo.increment_keys(user_id)
        except Exception as e:
            logger.error(f'Error when incrementing the total number of keys for user_id={user_id}: {e}')
            return False

    @staticmethod
    async def increment_daily_requests(user_id: int, user_key_repo: UserKeyRepository) -> bool:
        try:
            return await user_key_repo.increment_daily_requests(user_id)
        except Exception as e:
            logger.error(f'Error when incrementing daily requests for user_id={user_id}: {e}')
            return False

    @staticmethod
    async def validate_user_request(user_id: int, user_status: str, user_key_repo: UserKeyRepository) -> dict:
        """Check all conditions for key generation."""
        try:
            # Checking the daily limit
            if not await UserKeyService._check_daily_limit(user_id, user_status, user_key_repo):
                return {'can_generate': False, 'reason': 'daily_limit_exceeded', 'remaining_time': None}

            # Check request interval
            remaining_time_seconds = await UserKeyService._check_request_interval(user_id, user_status, user_key_repo)
            if remaining_time_seconds is not None:
                remaining_time = format_seconds_to_minutes_and_seconds(remaining_time_seconds)
                return {'can_generate': False, 'reason': 'interval_not_met', 'remaining_time': remaining_time}

            # All conditions are met
            return {'can_generate': True, 'reason': None, 'remaining_time': None}

        except Exception as e:
            logger.error(f'Error when checking key generation conditions for user_id={user_id}: {e}')
            return {'can_generate': False, 'reason': 'error', 'remaining_time': None}

    @staticmethod
    async def _check_daily_limit(user_id: int, user_status: str, user_key_repo: UserKeyRepository) -> bool:
        """Check the daily key limit has not been reached."""
        try:
            today_keys = await user_key_repo.get_daily_requests(user_id)
            daily_limit = STATUS_LIMITS[user_status]['daily_limit']
            if today_keys is not None and today_keys < daily_limit:
                return True
            return False
        except Exception as e:
            logger.error(f'Error when checking daily key limit for user_id={user_id}: {e}')
            return False

    @staticmethod
    async def _check_request_interval(user_id: int, user_status: str, user_key_repo: UserKeyRepository) -> Optional[int]:
        """Check the interval between key requests."""
        try:
            last_request = await user_key_repo.get_last_request_datetime(user_id)
            interval_minutes = STATUS_LIMITS[user_status]['interval_minutes']
            if last_request is not None:
                current_time = get_current_time()
                elapsed_time = (current_time - last_request).total_seconds()
                interval_seconds = interval_minutes * 60

                if elapsed_time >= interval_seconds:
                    return None
                else:
                    return int(interval_seconds - elapsed_time)
            return None
        except Exception as e:
            logger.error(f'Error when checking query interval for user_id={user_id}: {e}')
            return None
