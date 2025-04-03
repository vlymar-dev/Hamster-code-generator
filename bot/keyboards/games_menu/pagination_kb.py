from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers import PaginationCallbackData
from bot.keyboards.main_menu_kb import back_to_main_menu_button


def get_pagination_kb(current_page: int, total_pages: int, game_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_page > 1:
        builder.add(
            InlineKeyboardButton(
                text=_('⬅️ Back'),
                callback_data=PaginationCallbackData(game_name=game_name, current_page=current_page - 1).pack()
            )
        )

    builder.add(
        InlineKeyboardButton(
            text=_('Page {current_page} of {total_pages}').format(
                current_page=current_page,
                total_pages=total_pages
            ),
            callback_data='noop'
        )
    )

    if current_page < total_pages:
        builder.add(
            InlineKeyboardButton(
                text=_('➡️ Forward'),
                callback_data=PaginationCallbackData(game_name=game_name, current_page=current_page + 1).pack()
            )
        )

    builder.adjust(3)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
