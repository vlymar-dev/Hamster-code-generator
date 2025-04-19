import logging

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
from infrastructure.db.repositories import PromoCodeRepository, UserRepository
from infrastructure.services import CacheService, UserCacheService

logger = logging.getLogger(__name__)
admin_router = Router()


@admin_router.callback_query(F.data == 'manage_users')
async def manage_users_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    """Display user management statistics."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} accessed user management')

    try:
        await callback_query.message.delete()
        users_count = await UserRepository.get_users_count(session)
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('Total users: {users_count}').format(users_count=users_count), reply_markup=admin_panel_users_kb()
        )
    except Exception as e:
        logger.error(f'User management error for admin {admin_id}: {e}', exc_info=True)
        raise


@admin_router.callback_query(F.data == 'manage_keys')
async def manage_keys_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    """Display key usage statistics."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} accessed key management')

    try:
        await callback_query.answer()
        await callback_query.message.delete()
        today_keys = await UserRepository.get_today_keys_count(session)
        db_keys_count = await PromoCodeRepository.get_code_counts_for_games(session, HAMSTER_GAMES_LIST)
        db_keys_count_formated = '\n'.join(f'{count}.....<b>{game}</b>' for game, count in db_keys_count.items())
        await callback_query.message.answer(
            text=_('<b>Picked up the keys today:</b> {today_keys}\n\n' '🕹️ <i>All games:</i>\n' '{db_keys}').format(
                today_keys=today_keys, db_keys=db_keys_count_formated
            ),
            reply_markup=get_back_to_admin_panel_kb(),
        )
    except Exception as e:
        logger.error(f'Key management error for admin {admin_id}: {e}', exc_info=True)
        raise


@admin_router.callback_query(F.data == 'change_role')
async def add_role_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Initiate user role change process."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} started role change procedure')

    try:
        await callback_query.message.answer(
            text=_('🆔 <b>Enter user ID:</b>'), reply_markup=get_back_to_admin_panel_kb()
        )
        await callback_query.message.delete()
        await callback_query.answer()
        await state.set_state(AdminPanelState.target_user_id)
    except Exception as e:
        logger.error(f'Role change init error for admin {admin_id}: {e}', exc_info=True)
        raise


@admin_router.message(AdminPanelState.target_user_id)
async def process_change_role_handler(
    message: Message, state: FSMContext, session: AsyncSession, cache_service: CacheService
) -> None:
    """Process user ID input for role change."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} processing role change input')

    try:
        target_user_id = int(message.text)
        logger.info(f'Admin {admin_id} attempting to change role for user {target_user_id}')

        user_data = await UserCacheService.get_user_auth_data(
            cache_service=cache_service, session=session, user_id=target_user_id
        )
        current_user_role = user_data.user_role
        if not current_user_role:
            logger.warning(f'User {target_user_id} not found by admin {admin_id}')
            await message.delete()
            await message.answer(
                text=_(
                    '❗️ <b>Error changing user role.</b>\n\n'
                    'User <b><i>{target_user_id}</i></b> not found in DB.\n\n'
                    '<i>Retry entering the ID or return to the main menu</i>'
                ).format(target_user_id=target_user_id),
                reply_markup=get_back_to_admin_panel_kb(),
            )
            return

        await state.update_data(current_user_role=current_user_role, target_user_id=target_user_id)
        await message.answer(
            text=_(
                '👤\n\n<i>Current role:\n• <b>{current_role}</b></i>\n\n'
                '<i>Select a new role for user ID:\n• <b>{target_user_id}</b></i>'
            ).format(current_role=current_user_role, target_user_id=target_user_id),
            reply_markup=admin_panel_user_role_kb(current_user_role),
        )

    except ValueError:
        logger.warning(f'Invalid user ID input by admin {admin_id}')
        await message.delete()
        await message.answer(
            text=_("⚠️ <b>Oops!</b> Looks like it's not a number"),
            reply_markup=get_back_to_admin_panel_kb(),
        )
        return
    except Exception as e:
        logger.error(f'Role change processing error for admin {admin_id}: {e}', exc_info=True)
        raise


@admin_router.callback_query(F.data.startswith('change_role_to_'))
async def select_role_handler(
    callback_query: CallbackQuery, state: FSMContext, session: AsyncSession, cache_service: CacheService
) -> None:
    """Apply new user role changes."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} confirming role change')

    try:
        new_user_role = callback_query.data.split('_')[3]
        data = await state.get_data()
        target_user_id = int(data.get('target_user_id'))
        logger.info(f'Admin {admin_id} changing role for user {target_user_id} to {new_user_role}')

        await UserCacheService.update_user_auth_data(
            cache_service=cache_service, session=session, user_id=target_user_id, new_user_role=new_user_role
        )
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_(
                '🤩 <b>User role <i>updated!</i></b>\n\nNew role for user ID: <b>{target_user_id}</b> — '
                "<b><i>'{new_user_role}'</i></b>"
            ).format(target_user_id=target_user_id, new_user_role=new_user_role.capitalize()),
            reply_markup=get_back_to_admin_panel_kb(),
        )
    except Exception as e:
        logger.error(f'Role update error for admin {admin_id}: {e}', exc_info=True)
        raise


@admin_router.callback_query(F.data == 'back_to_admin_panel')
async def back_to_admin_panel_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Return to main admin panel view."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} returning to main panel')

    try:
        await state.clear()
        await callback_query.answer()
        await callback_query.message.delete()
        await show_admin_panel(callback_query.message)
    except Exception as e:
        logger.error(f'Admin panel return error for {admin_id}: {e}', exc_info=True)
        raise


async def show_admin_panel(message: Message) -> None:
    """Display main admin panel interface."""
    admin_id = message.from_user.id
    logger.info(f'Displaying admin panel for {admin_id}')
    await message.answer(
        text=_('👨‍💼💼 Admin Panel. Time to wield the power! (But shh... keep it secret!)'),
        reply_markup=admin_panel_kb(),
    )
