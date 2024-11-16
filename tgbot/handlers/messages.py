from aiogram.types import CallbackQuery, Message, Union
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.main_menu_kb import get_main_menu_kb


async def send_main_menu(event: Union[Message, CallbackQuery]) -> None:
    if isinstance(event, CallbackQuery):
        await event.message.delete()
        send_message = event.message.answer
    else:
        await event.delete()
        send_message = event.answer

    await send_message(
        text=_('What’s next? 🤔\n\n'
               '🎮 <b>Play and earn!</b> — Discover new combos, exciting games, and exclusive giveaways.  \n'
               '💥 <b>Stay tuned</b> for the latest news and events.\n'
               '📱 <b>Get your chance</b> for exclusive rewards!\n\n'
               '<b>Today users received:</b>\n'
               '🔹 <b>{keys_today}</b> <i>keys</i> 🔑\n\n'
               '🔥 <b>Choose an action below to keep climbing the leaderboard and join the elite players!</b>').format(
            keys_today='1',  # TODO: logic keys count
        ),
        reply_markup=get_main_menu_kb()
    )
