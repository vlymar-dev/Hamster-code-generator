import pytest
from aiogram.types import InlineKeyboardButton

from bot.keyboards.donation.donation_kb import (
    cancel_donation_button,
    get_cancel_donation_kb,
    get_confirm_donation_kb,
    get_donation_kb,
)


@pytest.mark.asyncio
async def test_get_donation_kb_structure():
    markup = await get_donation_kb()

    assert len(markup.inline_keyboard) == 3

    donate_buttons = markup.inline_keyboard[0]
    assert len(donate_buttons) == 3
    assert donate_buttons[0].text == '1 ⭐️'
    assert donate_buttons[0].callback_data == 'donate_1'
    assert donate_buttons[1].text == '10 🌟'
    assert donate_buttons[1].callback_data == 'donate_10'
    assert donate_buttons[2].text == '50 ✨'
    assert donate_buttons[2].callback_data == 'donate_50'

    custom_button = markup.inline_keyboard[1][0]
    assert 'Enter a Different Amount' in custom_button.text
    assert custom_button.callback_data == 'custom_donate'

    back_button = markup.inline_keyboard[2][0]
    assert 'Back to main menu' in back_button.text
    assert back_button.callback_data == 'back_to_main_menu'


@pytest.mark.asyncio
async def test_get_confirm_donation_db_structure():
    markup = await get_confirm_donation_kb()

    assert len(markup.inline_keyboard) == 2

    pay_button = markup.inline_keyboard[0][0]
    assert 'Give money' in pay_button.text
    assert pay_button.pay is True

    cancel_button = markup.inline_keyboard[1][0]
    assert "No it's scam" in cancel_button.text
    assert cancel_button.callback_data == 'cancel_payment'


def test_get_cancel_donation_kb_structure():
    markup = get_cancel_donation_kb()

    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1

    cancel_button = markup.inline_keyboard[0][0]
    assert 'Cancel payment' in cancel_button.text
    assert cancel_button.callback_data == 'cancel_payment'


def test_cancel_donation_button_structure():
    button = cancel_donation_button()

    assert isinstance(button, InlineKeyboardButton)
    assert 'Cancel payment' in button.text
    assert button.callback_data == 'cancel_payment'
