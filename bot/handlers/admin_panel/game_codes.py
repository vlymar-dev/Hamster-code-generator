import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.admin_panel.game_codes_kb import (
    get_admin_panel_codes_kb,
    get_cancel_game_code_action_kb,
    get_confirm_deletion_task_kb,
    get_game_codes_actions_kb,
)
from bot.states import GameCodeManagement
from infrastructure.db.repositories import GameTaskRepository
from infrastructure.schemas import GameTaskSchema

logger = logging.getLogger(__name__)
game_codes_router = Router()


@game_codes_router.callback_query(F.data == 'manage_codes')
async def manage_codes_handler(callback_query: CallbackQuery) -> None:
    """Show game selection menu for code management."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} entered code management')

    try:
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('<b>Choose a game:</b>'),
            reply_markup=get_admin_panel_codes_kb()
        )
    except Exception as e:
        logger.error(f'Manage codes error for {admin_id}: {str(e)}')
        raise


@game_codes_router.callback_query(F.data.startswith('admin_codes_for_'))
async def actions_with_game_codes_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle game selection and transition to action selection state."""
    admin_id = callback_query.from_user.id
    game_name: str = callback_query.data.split('_')[-1]
    logger.debug(f'Admin {admin_id} selected game: {game_name}')

    try:
        await state.update_data(selected_game=game_name)
        await state.set_state(GameCodeManagement.WaitingForActionSelection)
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('You have selected a game: <b>{game_name}</b>\n\nSelect an action:').format(game_name=game_name),
            reply_markup=get_game_codes_actions_kb()
        )
    except Exception as e:
        logger.error(f'Game selection undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.callback_query(F.data == 'add_code')
async def add_game_code_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Initiate process of adding new game code."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} triggered add_game_code_handler')

    try:
        data = await state.get_data()
        if 'selected_game' not in data:
            logger.warning(f'User {admin_id} tried to add code without selecting game')
            await callback_query.answer(
                text=_('⚠️ First, choose a game!'),
                show_alert=True)
            return
        logger.info(f'User {admin_id} started adding code for {data['selected_game']}')
        await state.set_state(GameCodeManagement.WaitingForTask)
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('🐥 Enter the task for the selected game:'),
            reply_markup=get_cancel_game_code_action_kb()
        )
    except Exception as e:
        logger.error(f'Adding code undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.message(GameCodeManagement.WaitingForTask)
async def process_task_input_handler(message: Message, state: FSMContext) -> None:
    """Process task input and validate length."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} entered task input stage')

    try:
        task = message.text
        if len(task) < 1:
            logger.warning(f'User {admin_id} entered empty task')
            await message.answer(
                text=_('⚠️ The length of a task must be longer than one character!'),
                reply_markup=get_cancel_game_code_action_kb()
            )
            return
        await state.update_data(task=task)
        await state.set_state(GameCodeManagement.WaitingForAnswer)
        await message.answer(
            text=_('⛱️ Enter an answer for the game:'),
            reply_markup=get_cancel_game_code_action_kb()
        )
    except Exception as e:
        logger.error(f'Task input undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.message(GameCodeManagement.WaitingForAnswer)
async def process_answer_input_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Process answer input and save new game code to database."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} entered answer input stage')

    try:
        answer = message.text
        if len(answer) <= 1:
            logger.warning(f'User {admin_id} entered short answer')
            await message.answer(
                text=_('⚠️ The length of a answer must be longer than one character!'),
                reply_markup=get_cancel_game_code_action_kb()
            )
            return

        data = await state.get_data()
        game_task = GameTaskSchema(
                game_name=data['selected_game'],
                task=data['task'],
                answer=answer
            )
        await GameTaskRepository.add_task(session, game_task)

        await state.clear()
        await message.answer(
            text=_('✅ <i>Code for the game <b>{game}</b> successfully added!</i>\n\n'
                   '🐥 <i>Task: <b>{task}</b></i>\n'
                   '⛱️ <i>Answer: <b>{answer}</b></i>\n\n'
                   'Select a game to add a new code or go back to the main menu:').format(
                game=game_task.game_name,
                task=game_task.task,
                answer=game_task.answer
            ),
            reply_markup=get_admin_panel_codes_kb()
        )
    except Exception as e:
        logger.error(f'Answer input undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.callback_query(F.data == 'delete_code')
async def delete_code_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Initiate process of deleting game code."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} triggered delete_code_handler')

    try:
        data = await state.get_data()
        if 'selected_game' not in data:
            logger.debug(f'Admin {admin_id} triggered delete_code_handler')

            await callback_query.answer(
                text=_('⚠️ First, choose a game!'),
                show_alert=True
            )
            return
        game_name = data['selected_game']
        await state.set_state(GameCodeManagement.WaitingForIDToDelete)
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('📲 You chose a game: <b>{game}</b>\n\n'
                   '📋 <b>Enter the ID to be deleted:</b>').format(game=game_name),
            reply_markup=get_cancel_game_code_action_kb()
        )
        logger.info(f'Admin {admin_id} started deletion process for {game_name}')
    except Exception as e:
        logger.error(f'Deletion code undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.message(GameCodeManagement.WaitingForIDToDelete)
async def process_delete_task_by_id_handler(message: Message, state: FSMContext, session: AsyncSession):
    """Process task ID input for deletion."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} entered ID input stage for deletion')

    try:
        try:
            task_id = int(message.text)
        except ValueError:
            logger.warning(f'Admin {admin_id} entered invalid ID: {message.text}')
            await message.answer(
                text=_('⚠️ Invalid <b>ID</b> format. Please enter a valid number!'),
                reply_markup=get_cancel_game_code_action_kb()
            )
            return
        await state.update_data(task_id=task_id)
        task: GameTaskSchema = await GameTaskRepository.get_task_by_id(session, task_id)
        if not task:
            logger.warning(f'Admin {admin_id} tried to delete non-existing task ID: {task_id}')
            await message.answer(
                text=_('⚠️ Task with ID <b>{task_id}</b> not found.\n\nRepeat input:').format(task_id=task_id),
                reply_markup=get_cancel_game_code_action_kb()
            )
            return
        await message.answer(
            text=_('⚠️ <b>Confirm the deletion of the task:</b>\n\n'
                   '📋 <b>ID:</b> {id}\n'
                   '<b>Task:</b> {task}\n'
                   '<b>Answer:</b> {answer}').format(
                id=task_id,
                task=task.task,
                answer=task.answer
            ),
            reply_markup=get_confirm_deletion_task_kb()
        )
        logger.info(f'Admin {admin_id} requested deletion confirmation for task ID: {task_id}')
    except Exception as e:
        logger.error(f'undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.callback_query(F.data == 'confirm_deletion')
async def confirmation_deletion_handler(
        callback_query: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
) -> None:
    """Handle final confirmation of task deletion."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} confirmed deletion')

    try:
        data = await state.get_data()
        task_id = data['task_id']

        if not task_id:
            logger.warning('No task_id found in state during deletion confirmation')
            await callback_query.answer(_('⚠️ Task ID not found!'), show_alert=True)
            return

        try:
            await GameTaskRepository.delete_task_by_id(session, task_id)
            await callback_query.message.answer(
                text=_('✅ Task with ID <b>{id}</b> successfully deleted!').format(id=task_id),
                reply_markup=get_admin_panel_codes_kb()
            )
        except Exception as err:
            logger.error(f'Error while deleting a record: {err}', exc_info=True)
            await callback_query.message.answer(
                text=_('❌ Task with ID <b>{id}</b> not found or could not be deleted.').format(id=task_id),
                reply_markup=get_cancel_game_code_action_kb()
            )
        await state.clear()
    except Exception as e:
        logger.error(f'Confirmation deletion undefined error for admin {admin_id}: {e}', exc_info=True)


@game_codes_router.callback_query(F.data == 'back_to_admin_game_menu')
async def back_to_admin_game_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle navigation back to game selection menu."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} navigated back to game menu')

    try:
        await state.clear()
        await show_game_selection_menu(callback_query)
        logger.debug(f'Admin {admin_id} navigated back to game menu')
    except Exception as e:
        logger.error(f'Back to admin panel undefined error for admin {admin_id}: {e}', exc_info=True)


async def show_game_selection_menu(callback_query: CallbackQuery) -> None:
    """Display game selection menu."""
    admin_id = callback_query.from_user.id

    try:
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('<b>📲 Choose a game:</b>'),
            reply_markup=get_admin_panel_codes_kb()
        )
    except Exception as e:
        logger.error(f'Show game selection undefined error for admin{admin_id}: {e}', exc_info=True)
