from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def get_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('Change language 🌍'), callback_data='change_language'))
    builder.row(back_to_main_menu_button())
    menu_markup = builder.as_markup()
    return menu_markup
