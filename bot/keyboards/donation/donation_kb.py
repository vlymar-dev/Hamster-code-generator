from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu_kb import back_to_main_menu_button


async def get_donation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text='1 ⭐️', callback_data='donate_1'),
        InlineKeyboardButton(text='10 🌟', callback_data='donate_10'),
        InlineKeyboardButton(text='50 ✨', callback_data='donate_50'),
    )
    builder.row(InlineKeyboardButton(text=_('💫 Enter a Different Amount'), callback_data='custom_donate'))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


async def get_confirm_donation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_('Give money'), pay=True))
    builder.row(InlineKeyboardButton(text=_('No it\'s scam'), callback_data='cancel_payment'))
    return builder.as_markup()


def get_cancel_donation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_donation_button()]])


def cancel_donation_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_('Cancel payment'), callback_data='cancel_payment')