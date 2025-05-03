from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button


def get_admin_feedback_kb(user_id: int, message_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('↩️ Reply to user'), callback_data=f'reply_to_user:{user_id}:{message_id}'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()
