from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import UserRepository


class IsBannedFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        user_id = obj.from_user.id if hasattr(obj, 'from_user') else None
        if not user_id:
            return False
        is_banned = await UserRepository.is_user_banned(session, user_id)
        if is_banned:
            text = _('🚫 You are blocked.')
            if isinstance(obj, Message):
                await obj.answer(text)
            elif isinstance(obj, CallbackQuery):
                await obj.answer(text, show_alert=True)
            return False
        return True
