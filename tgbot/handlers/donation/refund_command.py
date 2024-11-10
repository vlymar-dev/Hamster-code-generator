import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.handlers.messages import send_main_menu
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard

router = Router()


@router.message(F.text.startswith('/refund_stars'))
async  def refund_stars_command_handler(message: Message) -> None:
    transaction_id: str = message.text.split(' ')[1] if len(message.text.split()) > 1 else None

    if not transaction_id:
        await message.answer(
            _('To refund ⭐️ use the command <code><b>/refund_stars <i>transaction_id</i></b></code>')
        )
        return
    try:
        await message.bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id,
        )
        await message.answer(
            text=_('Return transaction completed ⏎'),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    except TelegramBadRequest as error:
        if 'CHARGE_NOT_FOUND' in error.message:
            await message.answer(
                _('❌ <b>Transaction with this number not found. Please check your input!</b>')
            )
        elif 'CHARGE_ALREADY_REFUNDED' in error.message:
            await message.answer(
                _('⚠️ <b>This transaction has already been refunded!!</b>')
            )
            await asyncio.sleep(2)
            await send_main_menu(message)
        else:
            await message.answer(
                _('❗️ <b>Error:</b> {error}').format(error=error.message)
            )


def register_refund_command_handler(dp) -> None:
    dp.include_router(router)