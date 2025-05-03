from unittest.mock import patch

import pytest


@pytest.fixture
def mock_referral_links(monkeypatch, request):
    num_links = getattr(request, 'param', 6)
    test_links = {f'Game{i}': f'url{i}' for i in range(num_links)}
    monkeypatch.setattr('bot.utils.referral.REFERRAL_LINKS', test_links)
    return test_links


@pytest.fixture
def mock_languages_dict(monkeypatch, request):
    if hasattr(request, 'param'):
        test_langs = (
            request.param if isinstance(request.param, dict) else {f'code{i}': f'Lang{i}' for i in range(request.param)}
        )
    else:
        test_langs = {}

    monkeypatch.setattr('bot.utils.static_data.LANGUAGES_DICT', test_langs)
    return test_langs


@pytest.fixture
def mock_games_dict(monkeypatch):
    test_games = {
        'cats': '🐈‍⬛ Cats Codes',
        'dogs': '🐕 Dogs Codes',
        'birds': '🐦 Birds Codes',
        'fish': '🐟 Fish Codes',
    }
    monkeypatch.setattr('bot.utils.static_data.GAME_TASKS_DICT', test_games)
    return test_games


@pytest.fixture
def mock_config():
    with patch('bot.keyboards.progress_kb.config') as mock:
        mock.telegram.generate_referral_link.return_value = 'https://t.me/test_bot?start=ref123'
        yield mock
