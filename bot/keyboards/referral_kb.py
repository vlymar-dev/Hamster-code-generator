from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button
from bot.utils import referral


def referral_links_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for game_name, game_url in referral.REFERRAL_LINKS.items():
        builder.button(
            text=game_name,
            url=game_url,
        )
    builder.adjust(2)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
