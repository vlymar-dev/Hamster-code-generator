import pytest
from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.admin_panel import (
    admin_panel_kb,
    admin_panel_user_role_kb,
    admin_panel_users_kb,
    get_back_to_admin_panel_kb,
)


def test_admin_panel_kb_structure():
    markup = admin_panel_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 3

    buttons_text = [btn.text for row in markup.inline_keyboard for btn in row]
    expected_texts = ['🔑 Keys', '🕹️ Codes', '🧑‍💻 Users', '📣 Announcements', '🔙 Back to main menu']
    assert buttons_text == expected_texts

    callback_datas = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    expected_callbacks = ['manage_keys', 'manage_codes', 'manage_users', 'manage_announcements', 'back_to_main_menu']
    assert callback_datas == expected_callbacks


def test_admin_panel_users_kb_structure():
    markup = admin_panel_users_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 2

    first_row = markup.inline_keyboard[0]
    assert first_row[0].text == '👑 Change Role'
    assert first_row[0].callback_data == 'change_role'

    back_row = markup.inline_keyboard[1]
    assert back_row[0].text == '🔙 Back to admin panel'
    assert back_row[0].callback_data == 'back_to_admin_panel'


@pytest.mark.parametrize(
    'current_role,expected_roles',
    [
        ('user', ['Admin', 'Moderator']),
        ('admin', ['User', 'Moderator']),
        ('moderator', ['User', 'Admin']),
    ],
)
def test_admin_panel_user_role_kb(current_role, expected_roles):
    markup = admin_panel_user_role_kb(current_user_role=current_role)

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) >= 1

    role_buttons = [btn for row in markup.inline_keyboard[:-1] for btn in row]
    assert all(btn.text in expected_roles for btn in role_buttons)

    for btn in role_buttons:
        assert btn.callback_data.startswith('change_role_to_')

    back_row = markup.inline_keyboard[-1]
    assert back_row[0].text == '🔙 Back to admin panel'
    assert back_row[0].callback_data == 'back_to_admin_panel'


def test_get_back_to_admin_panel_kb():
    markup = get_back_to_admin_panel_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1

    button = markup.inline_keyboard[0][0]
    assert button.text == '🔙 Back to admin panel'
    assert button.callback_data == 'back_to_admin_panel'
