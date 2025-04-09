from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from aiogram.utils.i18n import gettext as _

from bot.keyboards.feedback_kb import get_admin_feedback_kb
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from bot.states import AdminReplyToFeedback, UserLeaveFeedback
from core import config

feedback_router = Router()


@feedback_router.callback_query(F.data == 'feedback')
async def start_feedback_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await state.set_state(UserLeaveFeedback.writing_feedback)
    await callback_query.message.answer(
        text=_('💬 We’d love to hear your feedback! Please type your message below:'),
        reply_markup=get_back_to_main_menu_keyboard()
    )


@feedback_router.message(UserLeaveFeedback.writing_feedback)
async def process_user_feedback_message(message: Message, bot: Bot) -> None:
    if len(message.text) > 1:
        await message.answer(
            text=_('💖 Thank you for your feedback!\n'
                   'We really appreciate you taking the time to share your thoughts with us. 💕'),
            reply_markup=get_back_to_main_menu_keyboard()
        )
        for admin_id in config.telegram.ADMIN_ACCESS_IDs:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=_('📨 New feedback received!\n\n') + 'From: {username}\n'.format(
                        username=message.from_user.username or message.from_user.full_name
                    ) + 'Message:\n\n{text}'.format(text=message.text),
                    reply_markup=get_admin_feedback_kb(
                        user_id=message.from_user.id,
                        message_id=message.message_id
                    )
                )
            except Exception as e:
                print(f'Failed to forward message to admin {admin_id}: {e}')

        if hasattr(message, 'react'):
            emoji = ReactionTypeEmoji(emoji='👀')
            await message.react([emoji])


@feedback_router.callback_query(F.data.startswith('reply_to_user'))
async def start_admin_reply_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    parts = callback_query.data.split(':')
    user_id = int(parts[1])

    await state.set_state(AdminReplyToFeedback.waiting_for_reply)
    await state.update_data(user_id=user_id)

    await callback_query.message.answer(_('✍️ Please type your reply to the user. It will be sent immediately.'))


@feedback_router.message(AdminReplyToFeedback.waiting_for_reply)
async def process_send_admin_reply(message: Message, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get('user_id')

    try:
        await bot.send_message(
            chat_id=user_id,
            text=_('👋 The admin has responded to your feedback:\n\n'
                   '{text}\n\n'
                   'Thanks again for reaching out to us! 💖').format(text=message.text),
            reply_markup=get_back_to_main_menu_keyboard()
        )
        await message.answer(
            text=_('✅ Your reply has been sent to the user!'),
            reply_markup=get_back_to_main_menu_keyboard()
        )
    except Exception as e:
        await message.answer(_('❌ Failed to send your message. '
                               'The user may have blocked the bot or cannot be reached:\n\n{e}').format(e=e))
    finally:
        await state.clear()
