from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository
from tgbot.config import config
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, user_repo: UserRepository):
        user_id = message.from_user.id
        user_role = await user_repo.get_user_role(user_id)

        if user_id == config.tg_bot.bot_settings.admin_id:
            return True

        if user_role != 'admin':
            await message.answer(
                text=_('🚫 Access Denied!'),
            reply_markup=get_back_to_main_menu_keyboard()
            )
            return False
        return True