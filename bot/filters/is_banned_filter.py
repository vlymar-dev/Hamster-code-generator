import logging

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import UserRepository

logger = logging.getLogger(__name__)


class IsBannedFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        user_id = obj.from_user.id if hasattr(obj, 'from_user') else None
        if not user_id:
            logger.error(f'Missing user_id in IsBannedFilter for object: {type(obj).__name__}')
            return False

        logger.debug(f'Checking ban status for user {user_id}')
        is_banned = await UserRepository.is_user_banned(session, user_id)

        if is_banned:
            logger.warning(f'Banned user {user_id} attempted interaction')
            text = _('🚫 You are blocked.')
            if isinstance(obj, Message):
                await obj.answer(text)
            elif isinstance(obj, CallbackQuery):
                await obj.answer(text, show_alert=True)
            return False

        logger.debug(f'User {user_id} is not banned')
        return True
