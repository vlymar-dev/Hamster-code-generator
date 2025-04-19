import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, LabeledPrice, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _

from bot.handlers.info import user_info_handler
from bot.keyboards.donation.donation_kb import get_cancel_donation_kb, get_confirm_donation_kb
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from bot.states.payment_state import PaymentState

logger = logging.getLogger(__name__)
donations_router = Router()


@donations_router.callback_query(F.data == 'custom_donate')
async def custom_donate_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle custom donation amount initialization."""
    user_id = callback_query.from_user.id
    logger.debug(f'Custom donation start for user {user_id}')

    try:
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(text=_('💫 Enter Your Amount'), reply_markup=get_cancel_donation_kb())
        await state.set_state(PaymentState.amount_entry)
    except Exception as e:
        logger.error(f'Custom donate undefined error for user {user_id}: {e}', exc_info=True)


@donations_router.message(PaymentState.amount_entry)
async def process_custom_donate(message: Message, state: FSMContext) -> None:
    """Validate and process custom donation amount."""
    user_id = message.from_user.id
    logger.debug(f'Processing custom amount from user {user_id}')

    try:
        try:
            amount: int = int(message.text)
            if not (1 <= amount <= 2500):
                logger.warning(f'Invalid amount {amount} from user {user_id}')
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
            logger.info(f'Valid amount {amount} from user {user_id}')
            await send_invoice_message(message, amount)
        except TelegramBadRequest as error:
            logger.warning(f'Non-numeric input from user {user_id}')
            await message.answer(_('❗️ <b>Error:</b> {error}').format(error=error.message))
    except Exception as e:
        logger.error(f' Process donate undefined error for user {user_id}: {e}', exc_info=True)


@donations_router.callback_query(F.data.startswith('donate_'))
async def donate_callback_handler(callback_query: CallbackQuery) -> None:
    """Handle predefined donation amounts."""
    user_id = callback_query.from_user.id
    amount = int(callback_query.data.split('_')[1])
    logger.info(f'Predefined donation {amount} from user {user_id}')
    try:
        await callback_query.message.delete()
        await callback_query.answer()
        await send_invoice_message(callback_query.message, amount)
    except Exception as e:
        logger.error(f'Predefined donation undefined error for user {user_id}: {e}', exc_info=True)


@donations_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Process payment pre-checkout validation."""
    user_id = pre_checkout_query.from_user.id
    logger.debug(f'Pre-checkout validation for user {user_id}')
    try:
        await pre_checkout_query.answer(ok=True)
    except Exception as e:
        logger.error(f'Pre-checkout undefined error for user {user_id}: {e}', exc_info=True)


@donations_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment_handler(message: Message) -> None:
    """Confirm successful payment processing."""
    user_id = message.from_user.id
    logger.info(f'Successful payment from user {user_id}')
    try:
        await message.answer(
            text=_('🥳 <b>Thank you! Your support helps us improve!</b> 🤗'),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    except Exception as e:
        logger.error(f'Success payment undefined error for user {user_id}: {e}', exc_info=True)


async def send_invoice_message(message: Message, amount: int) -> None:
    """Generate and send payment invoice."""
    user_id = message.from_user.id
    logger.debug(f'Sending invoice for {amount} to user {user_id}')

    try:
        prices = [LabeledPrice(label='XTR', amount=amount)]
        await message.answer_invoice(
            title=_('Support Our Community 🚀'),
            description=_('Your contribution of {amount} 🌟 helps us').format(amount=amount),
            prices=prices,
            provider_token='',
            payload='channel_support',
            currency='XTR',
            reply_markup=await get_confirm_donation_kb(),
        )
    except Exception as e:
        logger.error(f'Send invoice undefined error for user {user_id}: {e}', exc_info=True)


@donations_router.callback_query(F.data == 'cancel_payment')
async def cancel_payment_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle payment cancellation and cleanup."""
    user_id = callback_query.from_user.id
    logger.info(f'Payment cancelled by user {user_id}')
    try:
        await callback_query.answer()
        await state.clear()
        await user_info_handler(callback_query)
    except Exception as e:
        logger.error(f'Cancellation payment undefined error for user {user_id}: {e}', exc_info=True)
