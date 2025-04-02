from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.static_data import LANGUAGES_DICT
from bot.filters import IsBannedFilter
from bot.handlers.main_menu import send_main_menu
from bot.keyboards.settings.change_language_kb import get_change_language_kb
from bot.keyboards.settings.notifications_kb import notifications_kb
from bot.keyboards.settings.settings_kb import get_settings_kb
from bot.middlewares import CustomI18nMiddleware
from core import config
from db.repositories import ReferralsRepository, UserRepository

settings_router = Router()


@settings_router.callback_query(IsBannedFilter(), F.data == 'settings_menu')
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

@settings_router.callback_query(F.data == 'change_language')
async def change_language_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    await callback_query.message.delete()
    await callback_query.answer()

    current_language_code: str = await UserRepository.get_user_language(session, callback_query.from_user.id)
    current_language = LANGUAGES_DICT.get(current_language_code)

    await callback_query.message.answer(
        text=_('Current language: <b>{}</b>\n\n'
               '🌐 Select a language from the available languages:').format(current_language),
        reply_markup= get_change_language_kb(current_language_code)
    )

@settings_router.callback_query(IsBannedFilter(), F.data.startswith('set_lang:'))
async def update_language_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        i18n: CustomI18nMiddleware
) -> None:
    selected_language_code: str = callback_query.data.split(':')[1]
    selected_language_name = LANGUAGES_DICT.get(selected_language_code)
    await UserRepository.update_user_language(
        session=session,
        user_id=callback_query.from_user.id,
        selected_language_code=selected_language_code
    )
    # Set a new language for the current user
    i18n.ctx_locale.set(selected_language_code)
    await callback_query.answer(
        text=_('🌐 Language updated to: {}').format(selected_language_name),
        show_alert=True
    )
    await send_main_menu(callback_query.message, session)


@settings_router.callback_query(F.data == 'notifications')
async def notifications_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    is_subscribed = await UserRepository.get_subscription_status(session, callback_query.from_user.id)
    text = _('Your subscription status: Subscribed') if is_subscribed else _('Your subscription status: Unsubscribed')
    await callback_query.message.answer(
        text=text,
        reply_markup = notifications_kb(is_subscribed)
    )


@settings_router.callback_query(F.data == 'subscribe_confirm')
async def subscribe_confirm_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    await UserRepository.update_subscription_status(session=session, user_id=callback_query.from_user.id, is_subscribed=True)
    await callback_query.answer(
        text=_('You have successfully Subscribed for notifications.'),
        show_alert=True
    )
    await send_main_menu(callback_query, session)

@settings_router.callback_query(F.data == 'unsubscribe')
async def unsubscribe_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    referrals_count = await ReferralsRepository.get_count_user_referrals_by_user_id(
        session,
        callback_query.from_user.id
    )
    required_number_of_referrals = config.telegram.REFERRAL_THRESHOLD
    if referrals_count < required_number_of_referrals:
        await callback_query.answer(
            text=_('You do not meet the requirements to unsubscribe from notifications. 🚫\n'
                   'You must have at least {} referrals to unsubscribe from notifications 🫂').format(
                required_number_of_referrals
            ),
            show_alert=True
        )
        return await send_main_menu(callback_query, session)

    await UserRepository.update_subscription_status(session=session, user_id=callback_query.from_user.id, is_subscribed=False)
    await callback_query.answer(
        text=_('You have successfully unsubscribed from notifications.'),
        show_alert=True
    )
    await send_main_menu(callback_query, session)
