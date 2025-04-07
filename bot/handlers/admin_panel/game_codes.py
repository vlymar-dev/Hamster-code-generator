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
from core.schemas import GameTaskSchema
from db.repositories import GameTaskRepository

game_codes_router = Router()


@game_codes_router.callback_query(F.data == 'manage_codes')
async def manage_codes_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('<b>Choose a game:</b>'),
        reply_markup=get_admin_panel_codes_kb()
    )


@game_codes_router.callback_query(F.data.startswith('admin_codes_for_'))
async def actions_with_game_codes_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    game_name: str = callback_query.data.split('_')[-1]
    await state.update_data(selected_game=game_name)
    await state.set_state(GameCodeManagement.WaitingForActionSelection)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('You have selected a game: <b>{game_name}</b>\n\nSelect an action:').format(game_name=game_name),
        reply_markup=get_game_codes_actions_kb()
    )


@game_codes_router.callback_query(F.data == 'add_code')
async def add_game_code_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if 'selected_game' not in data:
        await callback_query.answer(
            text=_('⚠️ First, choose a game!'),
            show_alert=True)
        return
    await state.set_state(GameCodeManagement.WaitingForTask)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('🐥 Enter the task for the selected game:'),
        reply_markup=get_cancel_game_code_action_kb()
    )


@game_codes_router.message(GameCodeManagement.WaitingForTask)
async def process_task_input_handler(message: Message, state: FSMContext) -> None:
    task = message.text
    if len(task) < 1:
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


@game_codes_router.message(GameCodeManagement.WaitingForAnswer)
async def process_answer_input_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    answer = message.text
    if len(answer) <= 1:
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

@game_codes_router.callback_query(F.data == 'delete_code')
async def delete_code_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if 'selected_game' not in data:
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


@game_codes_router.message(GameCodeManagement.WaitingForIDToDelete)
async def process_delete_task_by_id_handler(message: Message, state: FSMContext, session: AsyncSession):
    try:
        task_id = int(message.text)
    except ValueError:
        await message.answer(
            text=_('⚠️ Invalid <b>ID</b> format. Please enter a valid number!'),
            reply_markup=get_cancel_game_code_action_kb()
        )
        return
    await state.update_data(task_id=task_id)
    task: GameTaskSchema = await GameTaskRepository.get_task_by_id(session, task_id)
    if not task:
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


@game_codes_router.callback_query(F.data == 'confirm_deletion')
async def confirmation_deletion_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    task_id = data['task_id']

    try:
        await GameTaskRepository.delete_task_by_id(session, task_id)
        await message.answer(
            text=_('✅ Task with ID <b>{id}</b> successfully deleted!').format(id=task_id),
            reply_markup=get_admin_panel_codes_kb()
        )
    except Exception as e:
        # TODO: logging
        print(f'Error while deleting a record: {e}')
        await message.answer(
            text=_('❌ Task with ID <b>{id}</b> not found or could not be deleted.').format(id=task_id),
            reply_markup=get_cancel_game_code_action_kb()
        )
    await state.clear()


@game_codes_router.callback_query(F.data == 'back_to_admin_game_menu')
async def back_to_admin_game_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await show_game_selection_menu(callback_query)


async def show_game_selection_menu(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('<b>📲 Choose a game:</b>'),
        reply_markup=get_admin_panel_codes_kb()
    )
