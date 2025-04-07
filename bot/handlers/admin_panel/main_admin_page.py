from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.static_data import HAMSTER_GAMES_LIST
from bot.keyboards.admin_panel import (
    admin_panel_kb,
    admin_panel_user_role_kb,
    admin_panel_users_kb,
    get_back_to_admin_panel_kb,
)
from bot.states import AdminPanelState
from db.repositories import PromoCodeRepository, UserRepository

admin_router = Router()


@admin_router.callback_query(F.data == 'manage_users')
async def manage_users_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    await callback_query.message.delete()
    users_count = await UserRepository.get_users_count(session)
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('Total users: {users_count}').format(users_count=users_count),
        reply_markup=admin_panel_users_kb()
    )


@admin_router.callback_query(F.data == 'manage_keys')
async def manage_keys_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    today_keys = await UserRepository.get_today_keys_count(session)
    db_keys_count = await PromoCodeRepository.get_code_counts_for_games(session, HAMSTER_GAMES_LIST)
    db_keys_count_formated = '\n'.join(f'{count}.....<b>{game}</b>' for game, count in db_keys_count.items())
    await callback_query.message.answer(
        text=_('<b>Picked up the keys today:</b> {today_keys}\n\n'
               '🕹️ <i>All games:</i>\n'
               '{db_keys}').format(today_keys=today_keys, db_keys=db_keys_count_formated),
        reply_markup=get_back_to_admin_panel_kb()
    )


@admin_router.callback_query(F.data == 'change_role')
async def add_role_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer(
        text=_('🆔 <b>Enter user ID:</b>'),
        reply_markup=get_back_to_admin_panel_kb()
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await state.set_state(AdminPanelState.target_user_id)


@admin_router.message(AdminPanelState.target_user_id)
async def process_change_role_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    try:
        target_user_id = int(message.text)
        current_user_role = await UserRepository.get_user_role(session, target_user_id)
        if not current_user_role:
            await message.delete()
            await message.answer(
                text=_('❗️ <b>Error changing user role.</b>\n\n'
                       'User <b><i>{target_user_id}</i></b> not found in DB.\n\n'
                       '<i>Retry entering the ID or return to the main menu</i>').format(
                    target_user_id=target_user_id
                ),
                reply_markup=get_back_to_admin_panel_kb()
            )
            return


        await state.update_data(
            current_user_role=current_user_role,
            target_user_id=target_user_id
        )
        await message.answer(
            text=_('👤\n\n<i>Current role:\n• <b>{current_role}</b></i>\n'
                   '<i>Select a new role for user ID:\n• <b>{target_user_id}</b></i>').format(
                current_role=current_user_role,
                target_user_id=target_user_id
            ),
            reply_markup=admin_panel_user_role_kb(current_user_role),
        )

    except ValueError:
        await message.delete()
        await message.answer(
            text=_('⚠️ <b>Oops!</b> Looks like it\'s not a number'),
            reply_markup=get_back_to_admin_panel_kb(),
        )
        return


@admin_router.callback_query(F.data.startswith('change_role_to_'))
async def select_role_handler(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    new_user_role = callback_query.data.split('_')[3]
    data = await state.get_data()
    target_user_id = int(data.get('target_user_id'))
    await UserRepository.update_user_role(
        session=session,
        user_id=target_user_id,
        new_user_role=new_user_role
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('🤩 <b>User role <i>updated!</i></b>\n\nNew role for user ID: <b>{target_user_id}</b> — '
                     '<b><i>\'{new_user_role}\'</i></b>').format(
            target_user_id=target_user_id,
            new_user_role=new_user_role.capitalize()
        ),
        reply_markup=get_back_to_admin_panel_kb()
    )


@admin_router.callback_query(F.data == 'back_to_admin_panel')
async def back_to_admin_panel_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.answer()
    await callback_query.message.delete()
    await show_admin_panel(callback_query.message)


async def show_admin_panel(message: Message) -> None:
    await message.answer(
        text=_('👨‍💼💼 Admin Panel. Time to wield the power! (But shh... keep it secret!)'),
        reply_markup=admin_panel_kb()
    )
