from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository
from tgbot.keyboards.admin_panel.admin_panel_kb import admin_panel_kb


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
        result = await user_repo.get_user_role(user_id)
        return result

    @staticmethod
    async def change_user_role(user_repo: UserRepository, user_id: int, new_user_role: str) -> str:
        result = await user_repo.change_user_role(user_id, new_user_role)
        if result == 'success':
            return _(f'🤩 <b>User role <i>updated!</i></b>\n\nNew role for <b>{user_id}</b> — '
                     f'<b><i>\'{new_user_role.capitalize()}\'</i></b>')
        if result == 'unchanged':
            return _(f'🔹 <b>User role already set as <i>{new_user_role.capitalize()}</i>.</b>')
        if result == 'user_not_found':
            return _(f'❗️ <b>Error changing user role.</b>\n\nUser <b><i>{user_id}</i></b> not found in DB.')
        return _('💢 Database error changing user role!')

    @staticmethod
    async def check_user_exists(user_repo: UserRepository, user_id: int) -> bool:
        return await user_repo.check_user_exists(user_id)
