from aiogram.types import InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def unsubscribe_notifications_kb():
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🔕 Stop Notifications'), callback_data='unsubscribe_confirmation'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()