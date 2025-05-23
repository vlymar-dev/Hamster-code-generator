from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button


def get_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🌍 Change language'), callback_data='change_language'))
    builder.row(InlineKeyboardButton(text=_('📣 Manage Notifications'), callback_data='notifications'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
