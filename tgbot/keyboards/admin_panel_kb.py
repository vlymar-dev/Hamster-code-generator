from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🔑 Keys'), callback_data='manage_keys'),
                InlineKeyboardButton(text=_('🧑‍💻 Users'), callback_data='manage_users'))
    builder.row(InlineKeyboardButton(text=_('📣 Announcements'), callback_data='announcements'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def admin_panel_users_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('👑 Add Role'), callback_data='add_role'))
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def admin_panel_user_role() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('Admin'), callback_data='change_role_to_admin'),
                InlineKeyboardButton(text=_('User'), callback_data='change_role_to_user'))
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def get_cancel_change_role_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_admin_panel_button()]])


def back_to_admin_panel_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_('🔙 Back to admin panel'), callback_data='back_to_admin_panel')
