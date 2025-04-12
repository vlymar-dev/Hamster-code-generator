from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button
from infrastructure import config


def get_progress_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    referral_link = config.telegram.generate_referral_link(user_id)

    builder.row(InlineKeyboardButton(
        text=_('📤 Share your referral link'),
        switch_inline_query=_(' 📌\n'
                              'Hi! 🌟 Join me in this awesome bot! 🚀\n'
                              '🎮 Unlock achievements\n'
                              '🎁 Collect rewards\n'
                              '👉 Start now: {ref_link}').format(ref_link=referral_link)
    ))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
