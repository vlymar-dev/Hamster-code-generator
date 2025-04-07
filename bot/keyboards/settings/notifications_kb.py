from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button


def notifications_kb(status: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status:
        builder.row(InlineKeyboardButton(text=_('🔕 Stop Notifications'), callback_data='unsubscribe'))
    else:
        builder.row(InlineKeyboardButton(text=_('🔔 On Notifications'), callback_data='subscribe_confirm'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()