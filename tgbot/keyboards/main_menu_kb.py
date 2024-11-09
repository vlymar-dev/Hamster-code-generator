from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('⚙️ Settings'), callback_data='settings_menu'),
                InlineKeyboardButton(text=_('📊 My Stats'), callback_data='user_stats'))
    builder.row(InlineKeyboardButton(text=_('🔑 GET Keys'), callback_data='get_keys'))
    builder.row(InlineKeyboardButton(text=_('ℹ Info'), callback_data='user_info'))
    menu_markup = builder.as_markup()
    return menu_markup


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_('🔙 Main menu'), callback_data='back_to_main_menu')
