from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


async def get_payment_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('Money, money'), callback_data='get_money_button'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
