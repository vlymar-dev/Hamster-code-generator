from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


async def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('Referral Links'), callback_data='referral_links'),
                InlineKeyboardButton(text=_('Best games'), callback_data='games'))

    menu_markup = builder.as_markup()
    return menu_markup
