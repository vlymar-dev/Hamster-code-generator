from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository
from tgbot.keyboards.admin_panel_kb import admin_panel_kb


class AdminPanelService:

    @staticmethod
    async def show_admin_panel(message: Message) -> None:
        await message.answer(
            text=_('👨‍💼💼 Admin Panel. Time to wield the power! (But shh... keep it secret!)'),
            reply_markup=admin_panel_kb()
        )

    @staticmethod
    async def manage_users(user_repo: UserRepository) -> int:
        result = await user_repo.get_users_count()
        return result

    @staticmethod
    async def get_user_role(user_repo: UserRepository, user_id: int) -> str:
        result = user_repo.get_user_role(user_id)
        return result

    @staticmethod
    async def change_user_role(user_repo: UserRepository, user_id: int, new_user_role: str) -> str:
        result = user_repo.change_user_role(user_id, new_user_role)
        if result:
            return _(f'🤩 User role updated. New role for {user_id} - {new_user_role}')
        return _('Error changing user role')
