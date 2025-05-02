from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.admin_panel.announcements_kb import (
    get_announcement_menu_kb,
    get_announcements_kb,
    get_back_to_announcement_details_kb,
    get_back_to_announcements_kb,
    get_cancel_announcement_action_kb,
    get_confirmation_broadcast_kb,
    get_confirmation_translate_deletion,
    get_languages_kb,
)


def test_get_announcements_kb_structure():
    markup = get_announcements_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(buttons) == 4

    expected_texts = ['➕ Create Announcement', '🔍 View Detail', '❌ Delete Announcement', '🔙 Back to admin panel']
    actual_texts = [btn.text for btn in buttons]
    assert actual_texts == expected_texts


def test_get_announcement_menu_kb_structure():
    markup = get_announcement_menu_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(buttons) == 6

    expected_texts = [
        '🥏 Create Translation',
        '🔍 View Translation',
        '✏️ Edit',
        '❌ Delete',
        '📤 Broadcast Announcement',
        '🔙 Back to announcements',
    ]
    actual_texts = [btn.text for btn in buttons]
    assert actual_texts == expected_texts


def test_get_languages_kb_structure():
    languages = {'en': 'English', 'ru': 'Русский', 'es': 'Español'}
    markup = get_languages_kb(languages, callback_prefix='translate_to')

    assert isinstance(markup, InlineKeyboardMarkup)

    buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(buttons) == 4

    expected_callback_datas = ['translate_to_en', 'translate_to_ru', 'translate_to_es', 'back_to_announcement_details']
    actual_callback_datas = [btn.callback_data for btn in buttons]
    assert actual_callback_datas == expected_callback_datas


def test_get_confirmation_translate_deletion_structure():
    markup = get_confirmation_translate_deletion()

    assert isinstance(markup, InlineKeyboardMarkup)
    buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(buttons) == 2

    assert buttons[0].text == '❌ Confirm deletion'
    assert buttons[0].callback_data == 'confirm_translation_deletion'
    assert buttons[1].callback_data == 'back_to_announcement_details'


def test_get_cancel_announcement_action_kb_structure():
    markup = get_cancel_announcement_action_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 1
    button = markup.inline_keyboard[0][0]
    assert button.text == '🔙 Cancel'
    assert button.callback_data == 'back_to_announcements'


def test_get_back_to_announcement_details_kb_structure():
    markup = get_back_to_announcement_details_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    button = markup.inline_keyboard[0][0]
    assert button.text == '🔙 Back'
    assert button.callback_data == 'back_to_announcement_details'


def test_get_back_to_announcements_kb_structure():
    markup = get_back_to_announcements_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    button = markup.inline_keyboard[0][0]
    assert button.text == '🔙 Back to announcements'
    assert button.callback_data == 'back_to_announcements'


def test_get_confirmation_broadcast_kb_structure():
    markup = get_confirmation_broadcast_kb()

    assert isinstance(markup, InlineKeyboardMarkup)
    buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(buttons) == 2

    assert buttons[0].text == '✅ Yes'
    assert buttons[0].callback_data == 'confirm_broadcast'

    assert buttons[1].text == '❌ No'
    assert buttons[1].callback_data == 'back_to_announcement_details'
