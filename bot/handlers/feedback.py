import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from aiogram.utils.i18n import gettext as _

from bot.common import ImageManager
from bot.keyboards.feedback_kb import get_admin_feedback_kb
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from bot.states import AdminReplyToFeedback, UserLeaveFeedback
from core import config

logger = logging.getLogger(__name__)
feedback_router = Router()


@feedback_router.callback_query(F.data == 'feedback')
async def start_feedback_handler(callback_query: CallbackQuery, state: FSMContext, image_manager: ImageManager) -> None:
    """Handle feedback initiation with image support."""
    user_id = callback_query.from_user.id
    logger.debug(f'User feedback request from user {user_id}')

    try:

        logger.info(f'User {user_id} started feedback process')

        await callback_query.answer()
        await callback_query.message.delete()
        image = image_manager.get_random_image('handlers')
        response_text = _('💬 We’d love to hear your feedback! Please type your message below:')

        if image:
            await callback_query.message.answer_photo(
                photo=image,
                caption=response_text,
                reply_markup=get_back_to_main_menu_keyboard()
            )
        else:
            logger.warning(f'No images available in feedback for user {user_id}')
            await callback_query.message.answer(
                text=response_text,
                reply_markup=get_back_to_main_menu_keyboard()
            )
        await state.set_state(UserLeaveFeedback.writing_feedback)
    except Exception as e:
        logger.error(f'Feedback init error for user {callback_query.from_user.id}: {str(e)}')
        raise

@feedback_router.message(UserLeaveFeedback.writing_feedback)
async def process_user_feedback_message(message: Message, bot: Bot, image_manager: ImageManager) -> None:
    """Process user feedback with image support for admin notifications."""

    try:
        user_id = message.from_user.id
        logger.info(f'Processing feedback from user {user_id}')

        if len(message.text) < 2:
            logger.warning(f'Short feedback message from user {user_id}')
            return

        # User confirmation
        image = image_manager.get_random_image('handlers')
        response_text = _('💖 Thank you for your feedback!\n'
                   'We really appreciate you taking the time to share your thoughts with us. 💕')

        if image:
            await message.answer_photo(
                photo=image,
                caption=response_text,
                reply_markup=get_back_to_main_menu_keyboard()
            )
        else:
            logger.warning(f'No feedback images available for user {user_id}')
            await message.answer(
                text=response_text,
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
                print(f'Failed to notify admin {admin_id}: {str(e)}')

        if hasattr(message, 'react'):
            logger.debug(f'Adding reaction to message {message.message_id}')
            emoji = ReactionTypeEmoji(emoji='👀')
            await message.react([emoji])
    except Exception as e:
        logger.error(f'Feedback processing error for user {message.from_user.id}: {str(e)}')
        raise


@feedback_router.callback_query(F.data.startswith('reply_to_user'))
async def start_admin_reply_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle admin reply initiation with image support."""

    try:
        await callback_query.answer()
        admin_id = callback_query.from_user.id
        logger.info(f'Admin {admin_id} started user reply process')

        parts = callback_query.data.split(':')
        user_id = int(parts[1])

        await callback_query.message.answer(_('✍️ Please type your reply to the user. It will be sent immediately.'))

        await state.set_state(AdminReplyToFeedback.waiting_for_reply)
        await state.update_data(user_id=user_id)
    except Exception as e:
        logger.error(f'Admin reply init error: {str(e)}')
        raise


@feedback_router.message(AdminReplyToFeedback.waiting_for_reply)
async def process_send_admin_reply(message: Message, bot: Bot, state: FSMContext, image_manager: ImageManager) -> None:
    """Process admin reply with image support."""

    try:
        admin_id = message.from_user.id
        data = await state.get_data()
        user_id = data.get('user_id')
        logger.info(f'Admin {admin_id} sending reply to user {user_id}')

        image = image_manager.get_random_image('handlers')
        response_text = _('👋 The admin has responded to your feedback:\n\n'
                       '{text}\n\n'
                       'Thanks again for reaching out to us! 💖').format(text=message.text)
        try:
            if image:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=image,
                    caption=response_text,
                    reply_markup=get_back_to_main_menu_keyboard()
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=response_text,
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
            logger.debug(f'State cleared for admin {admin_id}')
    except Exception as e:
        logger.error(f'Admin reply processing error: {str(e)}')
        raise
