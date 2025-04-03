from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.common.static_data import ROLES_DICT
from bot.keyboards.main_menu_kb import back_to_main_menu_button


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🔑 Keys'), callback_data='manage_keys'),
                InlineKeyboardButton(text=_('🕹️ Codes'), callback_data='manage_codes'),
                InlineKeyboardButton(text=_('🧑‍💻 Users'), callback_data='manage_users'))
    builder.row(InlineKeyboardButton(text=_('📣 Announcements'), callback_data='manage_announcements'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def admin_panel_users_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('👑 Change Role'), callback_data='change_role'))
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def admin_panel_user_role_kb(current_user_role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for role, title in ROLES_DICT.items():
        if role == current_user_role:
            continue

        builder.button(
            text=title,
            callback_data=f'change_role_to_{role}'
        )

    builder.adjust(2)
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def get_back_to_admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_admin_panel_button()]])


def back_to_admin_panel_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_('🔙 Back to admin panel'), callback_data='back_to_admin_panel')
