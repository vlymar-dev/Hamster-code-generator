from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from core import config
from db.repositories import UserRepository


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession):
        user_id = message.from_user.id
        user_role = await UserRepository.get_user_role(session, user_id)

        if user_id in config.telegram.ADMIN_ACCESS_IDs:
            return True

        if user_role != 'admin':
            await message.answer(
                text=_('🚫 Access Denied!'),
            reply_markup=get_back_to_main_menu_keyboard()
            )
            return False
        return True