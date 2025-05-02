import math

import pytest
from aiogram.types import InlineKeyboardMarkup

from bot.handlers import PaginationCallbackData
from bot.keyboards.games_menu.games_menu import get_games_codes_and_keys_kb
from bot.keyboards.games_menu.pagination_kb import get_pagination_kb


def test_games_kb_structure(mock_games_dict):
    markup = get_games_codes_and_keys_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 4

    game_buttons = [btn for row in markup.inline_keyboard[:2] for btn in row]
    assert len(game_buttons) == len(mock_games_dict)

    for btn in game_buttons:
        assert btn.callback_data.startswith('get_codes_for_')
        game_key = btn.callback_data.replace('get_codes_for_', '')
        assert btn.text == mock_games_dict[game_key]

    hamster_btn = markup.inline_keyboard[-2][0]
    assert hamster_btn.text == '🔑 Hamster keys'
    assert hamster_btn.callback_data == 'hamster_keys'

    back_button = markup.inline_keyboard[-1][0]
    assert back_button.callback_data == 'back_to_main_menu'
    assert back_button.text == '🔙 Back to main menu'


@pytest.mark.parametrize(
    'game_keys',
    [
        [],
        ['cats'],
        ['cats', 'dogs', 'birds', 'fish'],
        ['cats', 'dogs', 'birds', 'fish', 'snakes'],
    ],
)
def test_games_kb_various_sizes(game_keys, monkeypatch):
    test_games = {key: f'{key.capitalize()} Codes' for key in game_keys}
    monkeypatch.setattr('bot.utils.static_data.GAME_TASKS_DICT', test_games)

    markup = get_games_codes_and_keys_kb()
    game_rows = math.ceil(len(game_keys) / 2)
    expected_rows = game_rows + 2
    assert len(markup.inline_keyboard) == expected_rows


@pytest.mark.parametrize(
    'current_page,total_pages,game_name,expected_buttons',
    [
        (1, 5, 'cats', ['Page 1 of 5', '➡️ Forward']),
        (3, 5, 'dogs', ['⬅️ Back', 'Page 3 of 5', '➡️ Forward']),
        (5, 5, 'birds', ['⬅️ Back', 'Page 5 of 5']),
    ],
)
def test_pagination_kb(current_page, total_pages, game_name, expected_buttons):
    markup = get_pagination_kb(current_page, total_pages, game_name)

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 2

    pagination_buttons = markup.inline_keyboard[0]
    assert len(pagination_buttons) == len(expected_buttons)

    for btn, expected_text in zip(pagination_buttons, expected_buttons):
        assert expected_text in btn.text

        if 'Back' in expected_text:
            data = PaginationCallbackData.unpack(btn.callback_data)
            assert data.game_name == game_name
            assert data.current_page == current_page - 1
        elif 'Forward' in expected_text:
            data = PaginationCallbackData.unpack(btn.callback_data)
            assert data.game_name == game_name
            assert data.current_page == current_page + 1

    back_btn = markup.inline_keyboard[-1][0]
    assert back_btn.callback_data == 'back_to_main_menu'


def test_pagination_callback_data():
    cb = PaginationCallbackData(game_name='test', current_page=2)
    assert cb.pack() == 'page:test:2'
    unpacked = PaginationCallbackData.unpack('page:test:2')
    assert unpacked.game_name == 'test'
    assert unpacked.current_page == 2
