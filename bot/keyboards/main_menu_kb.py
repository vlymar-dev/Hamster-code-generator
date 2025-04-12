import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.common.referral import REFERRAL_LINKS


def get_random_referral_buttons() -> list[InlineKeyboardButton]:
    selected_buttons = random.sample(list(REFERRAL_LINKS.items()), 1)

    return [InlineKeyboardButton(text=game_name, url=game_url) for game_name, game_url in selected_buttons]


def get_main_menu_kb() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    # NOTE:
    # This is used to display a random referral link for the "Game of the Day".
    # If needed, you can uncomment or modify this to enable the dynamic button.
    # builder.row(InlineKeyboardButton(text=_('🚀 Game of the Day ➡'), callback_data='noop'),
    #             get_random_referral_buttons()[0])

    builder.row(InlineKeyboardButton(text=_('── 🎮 GAMES CATALOG ──'), callback_data='referral_links'))
    builder.row(InlineKeyboardButton(text=_('🔑 Keys & Video Codes 🕹️'), callback_data='get_games'))
    builder.row(InlineKeyboardButton(text=_('─── 👤 PROFILE ───'), callback_data='user_progress'))
    builder.row(InlineKeyboardButton(text=_('⚙️ Settings'), callback_data='settings_menu'),
                InlineKeyboardButton(text=_('💬 Feedback'), callback_data='feedback'),
                InlineKeyboardButton(text=_('ℹ Info'), callback_data='user_info'))
    return builder.as_markup()


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_('🔙 Back to main menu'), callback_data='back_to_main_menu')
