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
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware
from tgbot.services.user_progress import generate_user_progress

router = Router()


@router.callback_query(F.data.startswith('set_lang:'))
async def update_language_handler(callback_query: CallbackQuery, db: Database, i18n: CustomI18nMiddleware) -> None:
    selected_language_code = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id

    await db.update_user_language(user_id, selected_language_code)
    await callback_query.answer(text=_('Language updated!'))  # TODO: logic keys count

    i18n.ctx_locale.set(selected_language_code)

    await send_main_menu(callback_query.message)


@router.callback_query(F.data == 'user_info')
async def user_info_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('<b>Hello!</b> Explore crypto games and bonuses with our bot — stay ahead and earn more! 💪\n\n'
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
        text=_('Settings menu here'),
        reply_markup=get_settings_kb()
    )

@router.callback_query(F.data == 'change_language')
async def change_language_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer(text=_('Select a language from the available languages'))
    await callback_query.message.answer(text=_('Please choose a language:'), reply_markup= get_change_language_kb())


@router.callback_query(F.data == 'user_progress')
async def user_progress_handler(callback_query: CallbackQuery, db: Database) -> None:
    user_stats = await generate_user_progress(user_id=callback_query.from_user.id, db=db)
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
        text=_('Best projects 💣'),
        reply_markup=referral_links_kb(),
    )



@router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await send_main_menu(callback_query)



def register_callback_queries_handler(dp) -> None:
    dp.include_router(router)
