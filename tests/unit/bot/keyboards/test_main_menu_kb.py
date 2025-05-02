from unittest import mock

from bot.keyboards.main_menu_kb import get_main_menu_kb, get_random_referral_buttons


def test_main_menu_kb_structure():
    markup = get_main_menu_kb()

    assert markup.inline_keyboard is not None
    assert len(markup.inline_keyboard) == 4


def test_get_random_referral_buttons(mock_referral_links):
    with mock.patch('random.sample', lambda x, k: [list(x)[0]]):
        buttons = get_random_referral_buttons()
        assert len(buttons) == 1
        assert buttons[0].text == 'Game0'
        assert buttons[0].url == 'url0'
