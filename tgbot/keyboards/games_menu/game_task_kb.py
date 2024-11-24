from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def pagination_kb(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_page > 1:
        builder.add(
            InlineKeyboardButton(
                text='⬅️ Back',
                callback_data=f'page:{current_page - 1}'
            )
        )

    builder.add(
        InlineKeyboardButton(
            text=f'Page {current_page} of {total_pages}',
            callback_data='noop'
        )
    )

    if current_page < total_pages:
        builder.add(
            InlineKeyboardButton(
                text='➡️ Forward',
                callback_data=f'page:{current_page + 1}'
            )
        )

    builder.adjust(3)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
