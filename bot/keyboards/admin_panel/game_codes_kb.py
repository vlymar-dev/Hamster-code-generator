from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.common.static_data import GAME_TASKS_DICT
from bot.keyboards.admin_panel.admin_panel_kb import back_to_admin_panel_button


def get_admin_panel_codes_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for game_key, game_name in GAME_TASKS_DICT.items():
        builder.button(
            text=game_name,
            callback_data=f'admin_codes_for_{game_key}',
        )
    builder.adjust(2)
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def get_game_codes_actions_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=_('➕ Add Code'), callback_data='add_code'),
        InlineKeyboardButton(text=_('❌ Delete Code'), callback_data='delete_code'),
    )
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def get_cancel_game_code_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_('🔙 Cancel'), callback_data='back_to_admin_game_menu')]]
    )


def get_confirm_deletion_task_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('✅ Confirm'), callback_data='confirm_deletion'))
    builder.row(InlineKeyboardButton(text=_('❌ Cancel'), callback_data='back_to_admin_panel'))
    return builder.as_markup()
