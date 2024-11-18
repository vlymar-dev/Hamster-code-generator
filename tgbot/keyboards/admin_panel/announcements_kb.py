from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.admin_panel.admin_panel_kb import back_to_admin_panel_button


def get_announcements_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('➕ Create Announcement'), callback_data='create_announcement'))
    builder.row(InlineKeyboardButton(text=_('🔍 View Detail'), callback_data='view_announcement_detail'))
    builder.row(InlineKeyboardButton(text=_('❌ Delete Announcement'), callback_data='delete_announcement'))
    builder.row(back_to_admin_panel_button())
    return builder.as_markup()


def get_announcement_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('🥏 Create Translation'), callback_data='create_announcement_translation'),
                InlineKeyboardButton(text=_('🔍 View Translation'), callback_data='view_announcement_translation'))
    builder.row(InlineKeyboardButton(text=_('✏️ Edit'), callback_data='edit_announcement_translation'))
    builder.row(InlineKeyboardButton(text=_('📤 Broadcast Announcement'), callback_data='broadcast_announcement'))

    builder.row(cancel_announcement_action_button(_('🔙 Back to announcements')))
    return builder.as_markup()


def get_cancel_announcement_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_announcement_action_button(_('🔙 Cancel'))]])


def get_back_to_announcements_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_announcement_action_button(_('🔙 Back to announcements'))]])


def cancel_announcement_action_button(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data='back_to_announcements')