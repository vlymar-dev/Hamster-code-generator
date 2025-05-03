import pytest

from bot.keyboards.settings.change_language_kb import get_change_language_kb
from bot.keyboards.settings.notifications_kb import notifications_kb
from bot.keyboards.settings.settings_kb import get_settings_kb


def test_settings_kb_structure():
    markup = get_settings_kb()

    change_language_button = markup.inline_keyboard[0][0]
    notifications_button = markup.inline_keyboard[1][0]
    back_button = markup.inline_keyboard[2][0]

    assert markup.inline_keyboard is not None
    assert len(markup.inline_keyboard) == 3

    assert change_language_button.text == '🌍 Change language'
    assert change_language_button.callback_data == 'change_language'
    assert notifications_button.text == '📣 Manage Notifications'
    assert notifications_button.callback_data == 'notifications'
    assert back_button.text == '🔙 Back to main menu'
    assert back_button.callback_data == 'back_to_main_menu'


@pytest.mark.parametrize(
    'status',
    [True, False],
)
def test_notifications_kb_structure(status):
    markup = notifications_kb(status)
    back_button = markup.inline_keyboard[1][0]

    assert markup.inline_keyboard is not None
    assert len(markup.inline_keyboard) == 2

    assert back_button.text == '🔙 Back to main menu'
    assert back_button.callback_data == 'back_to_main_menu'

    if status:
        unsubscribe_button = markup.inline_keyboard[0][0]

        assert unsubscribe_button.text == '🔕 Stop Notifications'
        assert unsubscribe_button.callback_data == 'unsubscribe'
    else:
        subscribe_button = markup.inline_keyboard[0][0]

        assert subscribe_button.text == '🔔 On Notifications'
        assert subscribe_button.callback_data == 'subscribe_confirm'


@pytest.mark.parametrize(
    'mock_languages_dict, current_lang, expected_buttons',
    [
        ({'en': 'English', 'ru': 'Russian'}, 'en', ['Russian']),
        ({'en': 'English', 'ru': 'Russian'}, 'ru', ['English']),
        ({'en': 'English', 'ru': 'Russian', 'es': 'Spanish'}, 'en', ['Russian', 'Spanish']),
    ],
    indirect=['mock_languages_dict'],
)
def test_change_language_kb_structure(mock_languages_dict, current_lang, expected_buttons, telegram_user):
    user = telegram_user(123)
    user.language_code = current_lang

    markup = get_change_language_kb(user.language_code)

    language_buttons = []
    for row in markup.inline_keyboard[:-1]:
        for btn in row:
            language_buttons.append(btn)

    assert len(language_buttons) == len(expected_buttons)

    lang_name_to_code = {v: k for k, v in mock_languages_dict.items()}

    for btn, expected_text in zip(language_buttons, expected_buttons):
        assert btn.text == expected_text
        expected_code = lang_name_to_code[expected_text]
        assert btn.callback_data == f'set_lang:{expected_code}'

    back_button = markup.inline_keyboard[-1][0]
    assert back_button.text == '🔙 Back to main menu'
    assert back_button.callback_data == 'back_to_main_menu'


def test_empty_languages_structure(mock_languages_dict, telegram_user):
    user = telegram_user(123)
    markup = get_change_language_kb(user.language_code)

    assert len(markup.inline_keyboard) == 1
    assert markup.inline_keyboard[0][0].text == '🔙 Back to main menu'
    assert markup.inline_keyboard[0][0].callback_data == 'back_to_main_menu'
