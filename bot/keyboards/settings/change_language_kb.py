from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button
from bot.utils import static_data


def get_change_language_kb(current_language_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for lang_code, language_name in static_data.LANGUAGES_DICT.items():
        if lang_code == current_language_code:
            continue

        builder.button(text=language_name, callback_data=f'set_lang:{lang_code}')
    builder.adjust(2)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
