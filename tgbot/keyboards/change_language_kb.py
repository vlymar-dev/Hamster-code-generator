from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button
from tgbot.services.staticdata import LANGUAGES_DICT


def get_change_language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for lang_code, language_name in LANGUAGES_DICT.items():
        builder.button(
            text=language_name,
            callback_data=f'set_lang:{lang_code}'
        )
    builder.adjust(2)
    builder.row(back_to_main_menu_button())

    return builder.as_markup()
