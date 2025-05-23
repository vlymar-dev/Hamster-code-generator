import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from infrastructure import config
from infrastructure.services import CacheService, UserCacheService

logger = logging.getLogger(__name__)


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, session_without_commit: AsyncSession, cache_service: CacheService):
        user_id = message.from_user.id
        logger.debug(f'Admin check for user {user_id}')

        if user_id in config.telegram.ADMIN_ACCESS_IDs:
            logger.info(f'User {user_id} granted admin access via config')
            return True
        user_data = await UserCacheService.get_user_auth_data(cache_service, session_without_commit, user_id)
        user_role = user_data.user_role
        if user_role == 'admin':
            logger.info(f'User {user_id} has admin role in database')
            return True

        logger.warning(f'User {user_id} attempted admin access without permission')
        await message.answer(text=_('🚫 Access Denied!'), reply_markup=get_back_to_main_menu_keyboard())
        return False
