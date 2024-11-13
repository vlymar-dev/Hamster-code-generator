from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.keyboards.admin_panel_kb import admin_panel_kb


class AdminPanelService:

    @staticmethod
    async def show_admin_panel(message: Message) -> None:
        await message.answer(
            text=_('👨‍💼💼 Admin Panel. Time to wield the power! (But shh... keep it secret!)'),
            reply_markup=admin_panel_kb()
        )

    @staticmethod
    async def manage_users(db :Database) -> int:
        result = await db.get_users_count()
        return result