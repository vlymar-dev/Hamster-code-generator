import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common import ImageManager
from bot.handlers.main_menu import send_main_menu
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard

logger = logging.getLogger(__name__)
refund_router = Router()


@refund_router.message(F.text.startswith('/refund_stars'))
async def refund_stars_command_handler(message: Message, session: AsyncSession, image_manager: ImageManager) -> None:
    """Process star refund requests with transaction validation."""
    user_id = message.from_user.id
    logger.debug(f'Refund request from user {user_id}')

    transaction_id: str = message.text.split(' ')[1] if len(message.text.split()) > 1 else None
    if not transaction_id:
        logger.warning(f'Missing transaction ID from user {user_id}')
        await message.answer(_('To refund ⭐️ use the command <code><b>/refund_stars <i>transaction_id</i></b></code>'))
        return
    try:
        logger.info(f'Processing refund for transaction {transaction_id}')
        await message.bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id,
        )
        await message.answer(
            text=_('Return transaction completed ⏎'),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        logger.info(f'Successful refund for transaction {transaction_id}')
    except TelegramBadRequest as error:
        logger.error(f'Refund error for user {user_id}: {error.message}')
        if 'CHARGE_NOT_FOUND' in error.message:
            await message.answer(_('❌ <b>Transaction with this number not found. Please check your input!</b>'))
        elif 'CHARGE_ALREADY_REFUNDED' in error.message:
            await message.answer(_('⚠️ <b>This transaction has already been refunded!!</b>'))
            await asyncio.sleep(2)
            await send_main_menu(message, session, image_manager)
        else:
            await message.answer(_('❗️ <b>Error:</b> {error}').format(error=error.message))
    except Exception as e:
        logger.error(f'Refund undefined error for user {user_id}: {e}', exc_info=True)
        raise
