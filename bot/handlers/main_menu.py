import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Union
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common import ImageManager
from bot.filters import IsBannedFilter
from bot.keyboards.main_menu_kb import get_main_menu_kb
from core import config
from db.repositories import UserRepository

logger = logging.getLogger(__name__)
main_menu_router = Router()


@main_menu_router.callback_query(IsBannedFilter(), F.data == 'back_to_main_menu')
async def back_to_main_menu_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        image_manager: ImageManager
) -> None:
    """Handle return to main menu request."""
    try:
        await callback_query.answer()
        await state.clear()
        await send_main_menu(callback_query, session, image_manager)
    except Exception as e:
        logger.error(f"Error in main menu handler for user {callback_query.from_user.id}: {str(e)}")
        raise


async def send_main_menu(
        event: Union[Message, CallbackQuery],
        session: AsyncSession,
        image_manager: ImageManager
) -> None:
    """Send main menu with statistics and image."""
    try:
        user_id = event.from_user.id
        image = image_manager.get_random_image('handlers')

        # Delete previous message
        if isinstance(event, CallbackQuery):
            await event.message.delete()
            send_method = event.message.answer_photo if image else event.message.answer
            logger.debug(f'Deleted previous message for user {user_id}')
        else:
            await event.delete()
            send_method = event.answer_photo if image else event.answer
            logger.debug(f'Deleted original message for user {user_id}')

        keys_today = await UserRepository.get_today_keys_count(session)
        keys_with_coefficient = keys_today * config.telegram.POPULARITY_COEFFICIENT
        logger.debug(f'Calculated keys: {keys_with_coefficient} for user {user_id}')

        response_text = _('What’s next? 🤔\n\n'
                   '🎮 <b>Play and earn!</b> — Discover new combos, exciting games, and exclusive giveaways.  \n'
                   '💥 <b>Stay tuned</b> for the latest news and events.\n'
                   '📱 <b>Get your chance</b> for exclusive rewards!\n\n'
                   '<b>Today users received:</b>\n'
                   '🔹 <b>{keys_today}</b> <i>keys</i> 🔑\n\n'
                   '🔥 <b>Choose an action below to keep climbing the leaderboard and join the elite players!</b>').format(
                keys_today=keys_with_coefficient,
            )

        # Send message with image or text
        if image:
            await send_method(
                photo=image,
                caption=response_text,
                reply_markup=get_main_menu_kb()
            )
        else:
            logger.warning(f'No images available in main menu for user {user_id}')
            await send_method(
                text=response_text,
                reply_markup=get_main_menu_kb()
            )
    except Exception as e:
        logger.error(f'Failed to send main menu to user {event.from_user.id}: {e}', exc_info=True)
        raise
