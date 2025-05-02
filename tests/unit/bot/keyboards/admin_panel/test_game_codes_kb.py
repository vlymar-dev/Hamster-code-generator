from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.admin_panel.game_codes_kb import (
    get_admin_panel_codes_kb,
    get_cancel_game_code_action_kb,
    get_confirm_deletion_task_kb,
    get_game_codes_actions_kb,
)


def test_get_admin_panel_codes_kb_structure(mock_games_dict):
    markup = get_admin_panel_codes_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == 5

    game_buttons_text = [btn.text for btn in all_buttons[:-1]]
    expected_game_names = list(mock_games_dict.values())
    assert game_buttons_text == expected_game_names

    callback_datas = [btn.callback_data for btn in all_buttons[:-1]]
    expected_callbacks = [f'admin_codes_for_{key}' for key in mock_games_dict.keys()]
    assert callback_datas == expected_callbacks

    back_button = all_buttons[-1]
    assert back_button.text == '🔙 Back to admin panel'
    assert back_button.callback_data == 'back_to_admin_panel'


def test_get_game_codes_actions_kb_structure():
    markup = get_game_codes_actions_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == 3

    add_button = markup.inline_keyboard[0][0]
    delete_button = markup.inline_keyboard[0][1]
    back_button = markup.inline_keyboard[1][0]

    assert add_button.text == '➕ Add Code'
    assert add_button.callback_data == 'add_code'

    assert delete_button.text == '❌ Delete Code'
    assert delete_button.callback_data == 'delete_code'

    assert back_button.text == '🔙 Back to admin panel'
    assert back_button.callback_data == 'back_to_admin_panel'


def test_get_cancel_game_code_action_kb_structure():
    markup = get_cancel_game_code_action_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1

    button = markup.inline_keyboard[0][0]
    assert button.text == '🔙 Cancel'
    assert button.callback_data == 'back_to_admin_game_menu'


def test_get_confirm_deletion_task_kb_structure():
    markup = get_confirm_deletion_task_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == 2

    confirm_button = markup.inline_keyboard[0][0]
    cancel_button = markup.inline_keyboard[1][0]

    assert confirm_button.text == '✅ Confirm'
    assert confirm_button.callback_data == 'confirm_deletion'

    assert cancel_button.text == '❌ Cancel'
    assert cancel_button.callback_data == 'back_to_admin_panel'
