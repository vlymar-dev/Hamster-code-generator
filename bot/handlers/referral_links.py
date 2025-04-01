from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.referral_kb import referral_links_kb

referral_links_router = Router()


@referral_links_router.callback_query(F.data == 'referral_links')
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
