import pytest

from bot.keyboards.referral_kb import referral_links_kb


@pytest.mark.parametrize(
    'mock_referral_links, expected_rows', [(0, 1), (1, 2), (4, 3)], indirect=['mock_referral_links']
)
def test_referral_kb_rows(mock_referral_links, expected_rows):
    markup = referral_links_kb()
    assert len(markup.inline_keyboard) == expected_rows
