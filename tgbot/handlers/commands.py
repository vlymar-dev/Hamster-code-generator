from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.keyboards.main_menu_kb import get_main_menu_kb
from tgbot.keyboards.change_language_kb import get_change_language_kb

router = Router()


@router.message(CommandStart())
async def handle_start_command(message: Message, db: Database) -> Message:
    await message.answer(
        text=_('Hello, <b>{first_name}</b>!👋').format(first_name=message.from_user.first_name),
        reply_markup=get_main_menu_kb()
    )
    user = message.from_user
    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'language_code': user.language_code,
    }
    await db.add_user(user_data)


@router.message(Command('change_language'))
async def change_language_command(message: Message):
    await message.answer(text=_('Please choose a language:'), reply_markup= get_change_language_kb())


def register_commands_handler(dp) -> None:
    dp.include_router(router)
