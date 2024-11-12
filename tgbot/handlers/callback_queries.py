from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.config import config
from tgbot.database import Database
from tgbot.handlers.messages import send_main_menu
from tgbot.keyboards.change_language_kb import get_change_language_kb
from tgbot.keyboards.donation.donation_kb import get_donation_kb
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb
from tgbot.keyboards.referral_kb import referral_links_kb
from tgbot.keyboards.settings_kb import get_settings_kb
from tgbot.keyboards.manage_notifications_kb import unsubscribe_notifications_kb
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware
from tgbot.services.language_service import LanguageService
from tgbot.services.user_progress_service import UserProgressService
from tgbot.services.user_notifications_service import UserService

router = Router()


@router.callback_query(F.data.startswith('set_lang:'))
async def update_language_handler(callback_query: CallbackQuery, db: Database, i18n: CustomI18nMiddleware) -> None:
    selected_language_code = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    response_text = await LanguageService.update_language(
        user_id=user_id,
        language_code=selected_language_code,
        i18n=i18n,
        db=db
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
               '🎰 <b>GAMECENTER</b>:\n• Earn and grow with exclusive opportunities! 🎗️\n\n'
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


@router.callback_query(F.data == 'unsubscribe_notifications')
async def unsubscribe_notifications_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('<i>Are you sure you want to unsubscribe from notifications?</i> 🥹'),
        reply_markup=unsubscribe_notifications_kb()
    )


@router.callback_query(F.data == 'unsubscribe_confirmation')
async def unsubscribe_confirmation_handler(callback_query: CallbackQuery, db: Database) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    response_text = await UserService.unsubscribe_user(user_id=callback_query.from_user.id, db=db)
    await callback_query.message.answer(
        text=response_text,
        reply_markup=get_back_to_main_menu_keyboard()
    )

@router.callback_query(F.data == 'user_progress')
async def user_progress_handler(callback_query: CallbackQuery, db: Database) -> None:
    user_stats = await UserProgressService.generate_user_progress(user_id=callback_query.from_user.id, db=db)
    if not user_stats:
        await callback_query.answer(text="User data not found.", show_alert=True)
        return
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📊 <b>Progress:</b>\n\n'
               '🏆 <b><u>Level:</u></b>\n'
               '<i>{achievement_name}</i>\nYou\'re moving up! Keep going for exclusive rewards! 💥\n\n'
               '🔑 <b><i>Total Keys Generated:</i></b> <i>{keys_total}</i>\n'
               '📨 <b><i>Referrals:</i></b> <i>{referrals}</i>\n\n'
               '🥇 <b><u>Your status:</u></b>\n'
               '<i>{user_status}</i>\n'
               '🤩 The higher the status, the more bonuses you get!\n\n'
               '🎳 <b>Invite friends, earn keys, and reach new heights with us!</b> 🌍').format(
            achievement_name=user_stats['achievement_name'],
            keys_total=user_stats['keys_total'],
            referrals=user_stats['referrals'],
            user_status=user_stats['user_status'],
        ),
        reply_markup=get_back_to_main_menu_keyboard()
    )


@router.callback_query(F.data == 'get_keys')
async def get_keys_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Here keys'),
        reply_markup=get_main_menu_kb()
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



@router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_main_menu(callback_query)



def register_callback_queries_handler(dp) -> None:
    dp.include_router(router)
