from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.keyboards.main_menu_kb import get_main_menu_kb

router = Router()


@router.callback_query(F.data.startswith('set_lang:'))
async def update_language_handler(callback_query: CallbackQuery, db: Database) -> None:
    selected_language_code = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id

    await db.update_user_language(user_id, selected_language_code)
    await callback_query.answer(text=_('Language updated!'))
    await callback_query.message.answer(reply_markup=await get_main_menu_kb())


def register_callback_queries_handler(dp) -> None:
    dp.include_router(router)
