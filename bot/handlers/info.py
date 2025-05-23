import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.donation.donation_kb import get_donation_kb
from bot.utils import ImageManager
from infrastructure import config

logger = logging.getLogger(__name__)
info_router = Router()


@info_router.callback_query(F.data == 'user_info')
async def user_info_handler(callback_query: CallbackQuery, image_manager: ImageManager) -> None:
    """Handle user info request with donation options."""
    user_id = callback_query.from_user.id
    logger.debug(f'User info request from user {user_id}')

    try:
        await callback_query.message.delete()
        await callback_query.answer()

        image = image_manager.get_random_image('handlers')
        response_text = _(
            '<b>ℹ️ Info</b>\n\n'
            '<i>Explore crypto games and bonuses with our bot — stay ahead and earn more! </i>💪\n\n'
            '👤 <b>PROFILE:</b>\n'
            '• Track your achievements. 🎯\n'
            '• Raise your status and unlock new privileges! 🚀\n\n'
            '🎮 <b>GAMES CATALOG</b>:\n• Earn and grow with exclusive opportunities! 🎗️\n\n'
            '💡 <i>Enjoy the bot?</i> <b>Support us!</b> Payment info — <i>/paysupport</i>\n\n'
            '<b>USDT/Ton (TON):</b> <code>{ton_wallet}</code>\n'
            '<b>USDT (TRC20):</b> <code>{trc_wallet}</code>\n'
            '<i>(Tap to copy)</i> 📋\n\n'
            '📬 <i>Got questions or suggestions?</i> \n'
            '🖊️ <b><i>Message us:</i></b>  <a href="{support}">•Tap to connect•</a>\n'
            '🔥 <b>Together we will make this service even better and bigger!</b>'
        ).format(
            support=config.telegram.SUPPORT_LINK,
            ton_wallet=config.wallets.TON,
            trc_wallet=config.wallets.TRC,
        )
        if image:
            await callback_query.message.answer_photo(
                photo=image, caption=response_text, reply_markup=await get_donation_kb()
            )
        else:
            logger.warning(f'No images available in info for user {user_id}')
            await callback_query.message.answer(text=response_text, reply_markup=await get_donation_kb())
    except Exception as e:
        logger.error(f'Error processing user info request for {user_id}: {e}', exc_info=True)
        raise
