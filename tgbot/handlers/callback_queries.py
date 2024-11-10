from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.handlers.messages import send_main_menu
from tgbot.keyboards.change_language_kb import get_change_language_kb
from tgbot.keyboards.donation.donation_kb import get_donation_kb
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb
from tgbot.keyboards.referral_kb import referral_links_kb
from tgbot.keyboards.settings_kb import get_settings_kb
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware

router = Router()


@router.callback_query(F.data.startswith('set_lang:'))
async def update_language_handler(callback_query: CallbackQuery, db: Database, i18n: CustomI18nMiddleware) -> None:
    selected_language_code = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id

    await db.update_user_language(user_id, selected_language_code)
    await callback_query.answer(text=_('Language updated!'))

    i18n.ctx_locale.set(selected_language_code)

    await send_main_menu(callback_query.message)


@router.callback_query(F.data == 'user_info')
async def user_info_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Bot info'),
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


@router.callback_query(F.data == 'user_stats')
async def user_stats_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Here your stats'),
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
    await send_main_menu(callback_query.message)



def register_callback_queries_handler(dp) -> None:
    dp.include_router(router)
