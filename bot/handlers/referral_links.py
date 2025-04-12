import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.common import ImageManager
from bot.keyboards.referral_kb import referral_links_kb

logger = logging.getLogger(__name__)
referral_links_router = Router()


@referral_links_router.callback_query(F.data == 'referral_links')
async def referral_links_handler(callback_query: CallbackQuery, image_manager: ImageManager) -> None:
    """Handle referral links request by providing partner links and bonuses."""
    user_id = callback_query.from_user.id
    logger.debug(f'Referral links request from user {user_id}')

    try:
        await callback_query.message.delete()
        await callback_query.answer()

        image = image_manager.get_random_image('handlers')
        response_text = _('💎 <b>Join now and unlock exclusive bonuses!</b> '
                          'Be among the first to explore new projects and opportunities.\n'
                          '🚀 <i>These platforms are trusted and tested</i> — '
                          'I’m already using them successfully to earn, and now it’s your turn!\n\n'
                          '🏁 <b>Ready to start?</b> Tap the links below to seize these early-bird advantages.\n'
                          '🗓️ <i>The sooner you join, the sooner you can start earning!</i>\n\n'
                          '🌐 <i><b>Projects that inspire! Open to everyone:</b></i>')
        if image:
            await callback_query.message.answer_photo(
                photo=image,
                caption=response_text,
                reply_markup=referral_links_kb()
            )
        else:
            logger.warning(f'No images available in referral links for user {user_id}')
            await callback_query.message.answer(
                text=response_text,
                reply_markup=referral_links_kb()
            )
    except Exception as e:
        logger.error(f'Error processing referral links request for {user_id}: {e}', exc_info=True)
        raise
