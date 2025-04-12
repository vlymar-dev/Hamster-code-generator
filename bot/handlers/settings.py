import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common import ImageManager
from bot.common.static_data import LANGUAGES_DICT
from bot.filters import IsBannedFilter
from bot.handlers.main_menu import send_main_menu
from bot.keyboards.settings.change_language_kb import get_change_language_kb
from bot.keyboards.settings.notifications_kb import notifications_kb
from bot.keyboards.settings.settings_kb import get_settings_kb
from bot.middlewares import CustomI18nMiddleware
from core import config
from db.repositories import ReferralsRepository, UserRepository

logger = logging.getLogger(__name__)
settings_router = Router()


@settings_router.callback_query(IsBannedFilter(), F.data == 'settings_menu')
async def settings_menu_handler(callback_query: CallbackQuery, image_manager: ImageManager) -> None:
    """Display main settings menu."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} opened settings menu')

    try:
        await callback_query.message.delete()
        await callback_query.answer()

        image = image_manager.get_random_image('handlers')
        response_text = _('⚙️ <b>Settings</b>\n\n'
                          '🎮 <i>Adjust the bot to fit your preferences! '
                          'Choose an option below to customize your experience:</i>\n\n'
                          '🌐 <b>Change Language</b> — Switch to your preferred language for a smoother experience.\n'
                          '🔕 <b>Unsubscribe from Notifications</b> — '
                          'Manage your subscriptions and stay in control of what you receive.\n\n'
                          '🎨 Personalize to make your time here more enjoyable and tailored just for you!')
        if image:
            await callback_query.message.answer_photo(
                photo=image,
                caption=response_text,
                reply_markup=get_settings_kb()
            )
        else:
            logger.warning(f'No images available in settings for user {user_id}')
            await callback_query.message.answer(
                text=response_text,
                reply_markup=get_settings_kb()
            )
    except Exception as e:
        logger.error(f'Settings menu error for {user_id}: {e}', exc_info=True)
        raise


@settings_router.callback_query(F.data == 'change_language')
async def change_language_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    """Show language selection interface with current language."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} requested language change')

    try:
        current_language_code: str = await UserRepository.get_user_language(session, callback_query.from_user.id)
        current_language = LANGUAGES_DICT.get(current_language_code)
        logger.debug(f'Current language for {user_id}: {current_language}')

        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('Current language: <b>{}</b>\n\n'
                   '🌐 Select a language from the available languages:').format(current_language),
            reply_markup=get_change_language_kb(current_language_code)
        )
        logger.info(f'Sent language options to {user_id}')
    except Exception as e:
        logger.error(f'Language change error for {user_id}: {e}', exc_info=True)
        raise


@settings_router.callback_query(IsBannedFilter(), F.data.startswith('set_lang:'))
async def update_language_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        i18n: CustomI18nMiddleware,
        image_manager: ImageManager
) -> None:
    """Update user's language preference and refresh main menu."""
    user_id = callback_query.from_user.id
    selected_language_code: str = callback_query.data.split(':')[1]
    logger.debug(f'User {user_id} selecting language: {selected_language_code}')

    try:
        selected_language_name = LANGUAGES_DICT.get(selected_language_code)
        await UserRepository.update_user_language(
            session=session,
            user_id=callback_query.from_user.id,
            selected_language_code=selected_language_code
        )
        logger.debug(f'Updated language for {user_id} to {selected_language_code}')
        # Set a new language for the current user
        i18n.ctx_locale.set(selected_language_code)  # noqa
        await callback_query.answer(
            text=_('🌐 Language updated to: {}').format(selected_language_name),
            show_alert=True
        )
        await send_main_menu(callback_query.message, session, image_manager)
    except Exception as e:
        logger.error(f'Language update failed for {user_id}: {e}', exc_info=True)
        raise


@settings_router.callback_query(F.data == 'notifications')
async def notifications_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    """Display current notification subscription status."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} checking notifications')

    try:
        is_subscribed = await UserRepository.get_subscription_status(session, callback_query.from_user.id)
        status = _('Subscribed') if is_subscribed else _('Unsubscribed')
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('Your subscription status: {}').format(status),
            reply_markup=notifications_kb(is_subscribed)
        )
    except Exception as e:
        logger.error(f'Notifications error for {user_id}: {e}', exc_info=True)
        raise


@settings_router.callback_query(F.data == 'subscribe_confirm')
async def subscribe_confirm_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        image_manager: ImageManager
) -> None:
    """Confirm and activate notification subscription."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} confirming subscription')

    try:
        await UserRepository.update_subscription_status(
            session=session,
            user_id=callback_query.from_user.id,
            is_subscribed=True
        )
        await callback_query.answer(
            text=_('You have successfully Subscribed for notifications.'),
            show_alert=True
        )
        await send_main_menu(callback_query, session, image_manager)
    except Exception as e:
        logger.error(f'Subscription error for {user_id}: {e}', exc_info=True)
        raise


@settings_router.callback_query(F.data == 'unsubscribe')
async def unsubscribe_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        image_manager: ImageManager
) -> None:
    """Handle unsubscribe request with referral requirement check."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} attempting unsubscribe')

    try:
        referrals_count = await ReferralsRepository.get_count_user_referrals_by_user_id(
            session,
            callback_query.from_user.id
        )
        required_number_of_referrals = config.telegram.REFERRAL_THRESHOLD
        if referrals_count < required_number_of_referrals:
            logger.warning(f'Unsubscribe denied for {user_id} (referrals: {referrals_count})')
            await callback_query.answer(
                text=_('You do not meet the requirements to unsubscribe from notifications. 🚫\n'
                       'You must have at least {} referrals to unsubscribe from notifications 🫂').format(
                    required_number_of_referrals
                ),
                show_alert=True
            )
            return await send_main_menu(callback_query, session, image_manager)

        await UserRepository.update_subscription_status(
            session=session,
            user_id=callback_query.from_user.id,
            is_subscribed=False
        )
        await callback_query.answer(
            text=_('You have successfully unsubscribed from notifications.'),
            show_alert=True
        )
        await send_main_menu(callback_query, session, image_manager)
    except Exception as e:
        logger.error(f'Unsubscribe error for {user_id}: {e}', exc_info=True)
        raise
