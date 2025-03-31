from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, LabeledPrice, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _

from bot.handlers.info import user_info_handler
from bot.keyboards.donation.donation_kb import get_cancel_donation_kb, get_confirm_donation_kb
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from bot.states.payment_state import PaymentState

donations_router = Router()


@donations_router.callback_query(F.data == 'custom_donate')
async def custom_donate_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer(
        text=_('💫 Enter Your Amount'),
        reply_markup=get_cancel_donation_kb()
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await state.set_state(PaymentState.amount_entry)


@donations_router.message(PaymentState.amount_entry)
async def process_custom_donate(message: Message, state: FSMContext) -> None:
    try:
        amount: int = int(message.text)
        if not (1 <= amount <= 2500):
            await message.delete()
            await message.answer(
                text=_('❗️ Enter an amount from <b>1</b> to <b>2500</b>. We appreciate your support!'),
                reply_markup=get_cancel_donation_kb(),
            )
            return

    except ValueError:
        await message.delete()
        await message.answer(
            text=_('⚠️ Oops! That doesn’t seem to be a valid number. Please try again to support us.'),
            reply_markup=get_cancel_donation_kb(),
        )
        return
    try:
        await state.clear()
        await send_invoice_message(message, amount)
    except TelegramBadRequest as error:
        await message.answer(
            _('❗️ <b>Error:</b> {error}').format(error=error.message)
        )


@donations_router.callback_query(F.data.startswith('donate_'))
async def donate_callback_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    amount: int = int(callback_query.data.split('_')[1])
    await callback_query.answer()
    await send_invoice_message(callback_query.message, amount)


@donations_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@donations_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment_handler(message: Message) -> None:
    await message.answer(
        text=_('🥳 <b>Thank you! Your support helps us improve!</b> 🤗'),
        reply_markup=get_back_to_main_menu_keyboard()
    )


async def send_invoice_message(message: Message, amount: int) -> None:
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=_('Support Our Community 🚀'),
        description=_('Your contribution of {amount} 🌟 helps us').format(amount=amount),
        prices=prices,
        provider_token="",
        payload="channel_support",
        currency="XTR",
        reply_markup=await get_confirm_donation_kb(),
    )


@donations_router.callback_query(F.data == 'cancel_payment')
async def cancel_payment_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await state.clear()
    await user_info_handler(callback_query)
