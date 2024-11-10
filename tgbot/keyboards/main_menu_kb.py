import random

import aiogram.utils.i18n
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.services.referral import REFERRAL_LINKS


def get_random_referral_buttons() -> list[InlineKeyboardButton]:
    selected_buttons = random.sample(list(REFERRAL_LINKS.items()), 3)

    return [InlineKeyboardButton(text=game_name, url=game_url) for game_name, game_url in selected_buttons]


def get_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=aiogram.utils.i18n.gettext('🔥 My Projects'), callback_data='referral_links'))

    random_buttons = get_random_referral_buttons()
    builder.row(random_buttons[0])
    builder.row(random_buttons[1], random_buttons[2])
    builder.row(InlineKeyboardButton(text=aiogram.utils.i18n.gettext('🔑 GET Keys'), callback_data='get_keys'))
    builder.row(InlineKeyboardButton(text=aiogram.utils.i18n.gettext('⚙️ Settings'), callback_data='settings_menu'),
                InlineKeyboardButton(text=aiogram.utils.i18n.gettext('📊 My Stats'), callback_data='user_stats'))
    builder.row(InlineKeyboardButton(text=aiogram.utils.i18n.gettext('ℹ Info'), callback_data='user_info'))
    return builder.as_markup()


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=aiogram.utils.i18n.gettext('🔙 Back to main menu'), callback_data='back_to_main_menu')
