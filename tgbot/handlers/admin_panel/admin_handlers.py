from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository
from tgbot.keyboards.admin_panel_kb import admin_panel_user_role, admin_panel_users_kb, get_cancel_change_role_kb
from tgbot.services.admin_panel_service import AdminPanelService
from tgbot.states.admin_panel_state import AdminPanelState

router = Router()

@router.callback_query(F.data == 'manage_users')
async def manage_users_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    users_count = await AdminPanelService.manage_users(user_repo)
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Total users: {users_count}').format(users_count=users_count),
        reply_markup=admin_panel_users_kb()
    )

@router.callback_query(F.data == 'manage_keys')
async def manage_keys_handler(callback_query: CallbackQuery) -> None:
    ...

@router.callback_query(F.data == 'announcements')
async def announcements_handler(callback_query: CallbackQuery) -> None:
    ...


@router.callback_query(F.data == 'add_role')
async def add_role_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer(
        text=_('🆔 <b>Enter user ID:</b>'),
        reply_markup=get_cancel_change_role_kb()
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await state.set_state(AdminPanelState.change_role_user_id)


@router.message(AdminPanelState.change_role_user_id)
async def process_change_role_handler(message: Message, state: FSMContext, user_repo: UserRepository) -> None:
    try:
        user_id: int = int(message.text)
        user = await AdminPanelService.check_user_exists(user_repo, user_id)
        if not user:
            await message.delete()
            await message.answer(
                text=_(f'❗️ <b>Error changing user role.</b>\n\n'
                       f'User <b><i>{user_id}</i></b> not found in DB.\n\n'
                       f'<i>Retry entering the ID or return to the main menu</i>'),
                reply_markup=get_cancel_change_role_kb()
            )
            return
        await state.update_data(change_role_user_id=user_id)
        await message.answer(
            text=_(f'👤 <b>Select a role for the user: <i>{user_id}</i></b>'),
            reply_markup=admin_panel_user_role(),
        )

    except ValueError:
        await message.delete()
        await message.answer(
            text=_('⚠️ <b>Oops!</b> Looks like it\'s not a number'),
            reply_markup=get_cancel_change_role_kb(),
        )
        return

@router.callback_query(F.data.startswith('change_role_to_'))
async def select_role_handler(callback_query: CallbackQuery, state: FSMContext, user_repo: UserRepository) -> None:
    new_user_role = callback_query.data.split('_')[3]
    data = await state.get_data()
    user_id = int(data.get('change_role_user_id'))
    text = await AdminPanelService.change_user_role(user_repo, user_id, new_user_role)
    await callback_query.answer()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_cancel_change_role_kb()
    )


@router.callback_query(F.data == 'back_to_admin_panel')
async def back_to_admin_panel_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.answer()
    await callback_query.message.delete()
    await AdminPanelService.show_admin_panel(callback_query.message)



def register_admin_panel_callback_queries_handler(dp) -> None:
    dp.include_router(router)