from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.progress_kb import get_progress_keyboard


def test_get_progress_kb_structure(mock_config, telegram_user):
    user = telegram_user(123)
    markup = get_progress_keyboard(user.id)

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 2

    share_button = markup.inline_keyboard[0][0]
    assert isinstance(share_button, InlineKeyboardButton)
    assert '📤 Share your referral link' in share_button.text
    assert share_button.switch_inline_query is not None

    back_button = markup.inline_keyboard[1][0]
    assert '🔙 Back to main menu' in back_button.text
    assert back_button.callback_data == 'back_to_main_menu'


def test_referral_link_generation(mock_config):
    test_user_id = 123
    expected_link = 'https://t.me/test_bot?start=ref123'

    markup = get_progress_keyboard(test_user_id)
    share_button = markup.inline_keyboard[0][0]

    assert expected_link in share_button.switch_inline_query
    mock_config.telegram.generate_referral_link.assert_called_once_with(test_user_id)


def test_share_button_content(mock_config):
    markup = get_progress_keyboard(123)
    share_button = markup.inline_keyboard[0][0]

    assert 'https://t.me/test_bot?start=ref123' in share_button.switch_inline_query
