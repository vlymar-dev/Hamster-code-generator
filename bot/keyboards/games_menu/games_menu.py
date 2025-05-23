from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button
from bot.utils import static_data


def get_games_codes_and_keys_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for game_key, game_name in static_data.GAME_TASKS_DICT.items():
        builder.button(
            text=game_name,
            callback_data=f'get_codes_for_{game_key}',
        )
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text='🔑 Hamster keys', callback_data='hamster_keys'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
