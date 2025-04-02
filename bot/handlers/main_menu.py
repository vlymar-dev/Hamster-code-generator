from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, Union
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters import IsBannedFilter
from bot.keyboards.main_menu_kb import get_main_menu_kb
from core import config
from db.repositories import UserRepository

main_menu_router = Router()


@main_menu_router.callback_query(IsBannedFilter(), F.data == 'back_to_main_menu')
async def back_to_main_menu_handler(callback_query: CallbackQuery, session: AsyncSession):
    await callback_query.answer()
    await send_main_menu(callback_query, session)


async def send_main_menu(event: Union[Message, CallbackQuery], session: AsyncSession) -> None:
    if isinstance(event, CallbackQuery):
        await event.message.delete()
        send_message = event.message.answer
    else:
        await event.delete()
        send_message = event.answer
    keys_today = await UserRepository.get_today_keys_count(session)
    keys_with_coefficient = keys_today * config.telegram.POPULARITY_COEFFICIENT
    await send_message(
        text=_('What’s next? 🤔\n\n'
               '🎮 <b>Play and earn!</b> — Discover new combos, exciting games, and exclusive giveaways.  \n'
               '💥 <b>Stay tuned</b> for the latest news and events.\n'
               '📱 <b>Get your chance</b> for exclusive rewards!\n\n'
               '<b>Today users received:</b>\n'
               '🔹 <b>{keys_today}</b> <i>keys</i> 🔑\n\n'
               '🔥 <b>Choose an action below to keep climbing the leaderboard and join the elite players!</b>').format(
            keys_today=keys_with_coefficient,
        ),
        reply_markup=get_main_menu_kb()
    )
