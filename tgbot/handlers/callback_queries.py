import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.promo_code_repo import PromoCodeRepository
from infrastructure.repositories.referral_repo import ReferralRepository
from infrastructure.repositories.user_key_repo import UserKeyRepository
from infrastructure.repositories.user_repo import UserRepository
from tgbot.common.staticdata import HAMSTER_GAMES_LIST
from tgbot.config import config
from tgbot.handlers.messages import send_main_menu
from tgbot.keyboards.donation.donation_kb import get_donation_kb
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from tgbot.keyboards.progress_kb import get_progress_keyboard
from tgbot.keyboards.referral_kb import referral_links_kb
from tgbot.keyboards.settings.change_language_kb import get_change_language_kb
from tgbot.keyboards.settings.notifications_kb import notifications_kb
from tgbot.keyboards.settings.settings_kb import get_settings_kb
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware
from tgbot.services.promo_code_service import PromoCodeService
from tgbot.services.settings.user_language_service import UserLanguageService
from tgbot.services.settings.user_notifications_service import UserNotificationsService
from tgbot.services.user_key_service import UserKeyService
from tgbot.services.user_progress_service import UserProgressService

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('set_lang:'))
async def update_language_handler(callback_query: CallbackQuery, user_repo: UserRepository, i18n: CustomI18nMiddleware) -> None:
    selected_language_code = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    response_text = await UserLanguageService.update_language(
        user_id=user_id,
        language_code=selected_language_code,
        i18n=i18n,
        user_repo=user_repo
    )

    await callback_query.answer(text=response_text)

    await send_main_menu(callback_query.message)


@router.callback_query(F.data == 'user_info')
async def user_info_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('<b>ℹ️ Info</b>\n\n'
               '<i>Explore crypto games and bonuses with our bot — stay ahead and earn more! </i>💪\n\n'
               '📊 <b>Check Progress:</b>\n'
               '• Track your achievements. 🎯\n'
               '• Raise your status and unlock new privileges! 🚀\n\n'
               '🎰 <b>GAME CENTER</b>:\n• Earn and grow with exclusive opportunities! 🎗️\n\n'
               '💡 <i>Enjoy the bot?</i> <b>Support us!</b> Payment info — <i>/paysupport</i>\n\n'
               '<b>USDT/Ton (TON):</b> <code>{ton_wallet}</code>\n'
               '<b>USDT (TRC20):</b> <code>{trc_wallet}</code>\n'
               '<i>(Tap to copy)</i> 📋\n\n'
               '📬 <i>Got questions or suggestions?</i> \n'
               '🖊️ <b><i>Message us:</i></b>  <a href="{support}">•Tap to connect•</a>\n'
               '🔥 <b>Together we will make this service even better and bigger!</b>').format(
            support=config.tg_bot.bot_info.support_link,
            ton_wallet=config.tg_bot.wallets.ton_wallet,
            trc_wallet=config.tg_bot.wallets.trc_wallet,
        ),
        reply_markup=await get_donation_kb()
    )


@router.callback_query(F.data == 'settings_menu')
async def settings_menu_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('⚙️ <b>Settings</b>\n\n'
               '🎮 <i>Adjust the bot to fit your preferences! Choose an option below to customize your experience:</i>\n\n'
               '🌐 <b>Change Language</b> — Switch to your preferred language for a smoother experience.\n'
               '🔕 <b>Unsubscribe from Notifications</b> — Manage your subscriptions and stay in control of what you receive.\n\n'
               '🎨 Personalize to make your time here more enjoyable and tailored just for you!'),
        reply_markup=get_settings_kb()
    )

@router.callback_query(F.data == 'change_language')
async def change_language_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Select a language from the available languages'),
        reply_markup= get_change_language_kb()
    )


@router.callback_query(F.data == 'notifications')
async def notifications_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    text, status = await UserNotificationsService.get_subscription_status(
        user_id=callback_query.from_user.id,
        user_repo=user_repo
    )
    await callback_query.message.answer(
        text=text,
        reply_markup=notifications_kb(status)
    )


@router.callback_query(F.data == 'subscribe_confirm')
async def subscribe_confirm_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    response_text = await UserNotificationsService.subscribe_user(
        user_id=callback_query.from_user.id, user_repo=user_repo
    )
    await callback_query.message.answer(
        text=response_text,
        reply_markup=get_back_to_main_menu_keyboard()
    )

@router.callback_query(F.data == 'unsubscribe')
async def unsubscribe_handler(callback_query: CallbackQuery, user_repo: UserRepository, referral_repo: ReferralRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    response_text = await UserNotificationsService.unsubscribe_user(
        user_id=callback_query.from_user.id, user_repo=user_repo, referral_repo=referral_repo
    )
    await callback_query.message.answer(
        text=response_text,
        reply_markup=get_back_to_main_menu_keyboard()
    )

@router.callback_query(F.data == 'user_progress')
async def user_progress_handler(callback_query: CallbackQuery, user_repo: UserRepository, referral_repo: ReferralRepository) -> None:
    user_progress = await UserProgressService.generate_user_progress(
        user_id=callback_query.from_user.id, user_repo=user_repo, referral_repo=referral_repo
    )
    if not user_progress:
        await callback_query.answer(text="User data not found.", show_alert=True)
        return
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=user_progress,
        reply_markup=get_progress_keyboard(user_id=callback_query.from_user.id)
    )


@router.callback_query(F.data == 'referral_links')
async def referral_links_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('💎 <b>Join now and unlock exclusive bonuses!</b> '
               'Be among the first to explore new projects and opportunities.\n'
               '🚀 <i>These platforms are trusted and tested</i> — '
               'I’m already using them successfully to earn, and now it’s your turn!\n\n'
               '🏁 <b>Ready to start?</b> Tap the links below to seize these early-bird advantages.\n'
               '🗓️ <i>The sooner you join, the sooner you can start earning!</i>\n\n'
               '🌐 <i><b>Projects that inspire! Open to everyone:</b></i>'),
        reply_markup=referral_links_kb(),
    )


@router.callback_query(F.data == 'hamster_keys')
async def get_hamster_keys(callback_query: CallbackQuery, promo_code_repo: PromoCodeRepository, user_key_repo: UserKeyRepository) -> None:
    user_id: int = callback_query.from_user.id
    user_status: str = 'free'  # TODO: implement user status retrieval

    validation_result = await UserKeyService.validate_user_request(user_id, user_status, user_key_repo)
    if not validation_result['can_generate']:
        if validation_result['reason'] == 'daily_limit_exceeded':
            await callback_query.answer('You have reached your daily key limit.', show_alert=True)
            return
        elif validation_result['reason'] == 'interval_not_met':
            remaining_time = validation_result['remaining_time']
            minutes = remaining_time.get('min')
            seconds = remaining_time.get('sec')
            if minutes:
                time_text = _('⏱️ Wait for {minutes} min {seconds} sec before getting the next key.').format(
                    minutes=minutes, seconds=seconds
                )
            else:
                time_text = _('⏱️ Wait for {seconds} sec before getting the next key.').format(seconds=seconds)
            await callback_query.answer(time_text, show_alert=True)
            return

    promo_codes = await PromoCodeService.get_and_delete_promo_codes(HAMSTER_GAMES_LIST, promo_code_repo)
    text = []
    for game_name, promo_code in promo_codes.items():
        if promo_code:
            text.append(f'<b>{game_name}:</b>\n • <code>{promo_code}</code>\n')
        else:
            text.append(_('<b>{}:</b>\n • <i>No promo codes available 🥹</i>').format(game_name))

    formatted_text = '\n'.join(text)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('{text}\n\n🔖 (click to copy)').format(text=formatted_text),
        reply_markup=get_back_to_main_menu_keyboard()
    )
    await user_key_repo.increment_keys(user_id)
    await user_key_repo.increment_daily_requests(user_id)


@router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_main_menu(callback_query)


def register_callback_queries_handler(dp) -> None:
    dp.include_router(router)
