from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.config import config
from tgbot.keyboards.main_menu_kb import back_to_main_menu_button


def get_progress_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    referral_link = config.tg_bot.bot_info.generate_referral_link(user_id)

    builder.row(InlineKeyboardButton(
        text=_("📩 Invite a Friend"),
        switch_inline_query="Hi! 🌟 Join me in this awesome bot! 🚀\n"
                            "🎮 Unlock achievements\n"
                            "🎁 Collect rewards\n"
                            f"👉 Start now: {referral_link}"
    ))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
