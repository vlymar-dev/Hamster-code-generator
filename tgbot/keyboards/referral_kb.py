from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button
from tgbot.services.referral import REFERRAL_LINKS


def referral_links_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for game_name, game_url in REFERRAL_LINKS.items():
        builder.button(
            text=game_name,
            url=game_url,
        )
    builder.adjust(2)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
