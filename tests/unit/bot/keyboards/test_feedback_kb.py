from bot.keyboards.feedback_kb import get_admin_feedback_kb


def test_get_admin_feedback_kb_structure(telegram_user, telegram_message, telegram_chat):
    user = telegram_user(123)
    message = telegram_message(chat=telegram_chat, user=user)

    markup = get_admin_feedback_kb(user.id, message.message_id)
    back_button = markup.inline_keyboard[-1][0]

    assert markup.inline_keyboard is not None
    assert len(markup.inline_keyboard) == 2

    assert back_button.text == '🔙 Back to main menu'
    assert back_button.callback_data == 'back_to_main_menu'
