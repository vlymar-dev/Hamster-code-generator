from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.keyboards.admin_panel_kb import admin_panel_users_kb
from tgbot.services.admin_panel_service import AdminPanelService

router = Router()

@router.callback_query(F.data == 'manage_users')
async def manage_users_handler(callback_query: CallbackQuery, db: Database) -> None:
    users_count = await AdminPanelService.manage_users(db)
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Total users: {users_count}').format(users_count=users_count),
        reply_markup=admin_panel_users_kb()
    )

@router.callback_query(F.data == 'manage_keys')
async def manage_keys_handler(callback_query: CallbackQuery) -> None:
    ...

@router.callback_query(F.data == 'manage_notifications')
async def manage_notifications_handler(callback_query: CallbackQuery) -> None:
    ...


@router.callback_query(F.data == 'add_role')
async def add_role_handler(callback_query: CallbackQuery) -> None:
    ...


@router.callback_query(F.data == 'back_to_admin_panel')
async def back_to_admin_panel_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await AdminPanelService.show_admin_panel(callback_query.message)



def register_admin_panel_callback_queries_handler(dp) -> None:
    dp.include_router(router)