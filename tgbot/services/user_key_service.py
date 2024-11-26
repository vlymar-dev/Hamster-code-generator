import logging
from datetime import datetime
from typing import Optional

from aiogram.utils.i18n import gettext as _
from sqlalchemy.exc import DatabaseError

from infrastructure.repositories.referral_repo import ReferralRepository
from infrastructure.repositories.user_key_repo import UserKeyRepository
from infrastructure.repositories.user_repo import UserRepository

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
