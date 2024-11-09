from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from tgbot.keyboards.main_menu_kb import get_main_menu_kb



async def send_main_menu(message: Message) -> None:
    await message.delete()
    await message.answer(
        text=_('Main menu 👑'),
        reply_markup=await get_main_menu_kb()
    )
