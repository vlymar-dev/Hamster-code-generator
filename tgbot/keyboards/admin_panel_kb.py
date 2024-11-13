from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🔑 Keys'), callback_data='manage_keys'),
                InlineKeyboardButton(text=_('🧑‍💻 Users'), callback_data='manage_users'))
    builder.row(InlineKeyboardButton(text=_('📣 Manage Notifications'), callback_data='manage_notifications'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()