from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.game_task_repo import GameTaskRepository
from tgbot.keyboards.admin_panel.game_codes_kb import (
    get_admin_panel_codes_kb,
    get_cancel_game_code_action_kb,
    get_game_codes_actions_kb,
)
from tgbot.services.game_task_service import GameTaskService
from tgbot.states.game_code_state import GameCodeManagement

router = Router()


@router.callback_query(F.data == 'manage_codes')
async def manage_codes_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('<b>Choose a game:</b>'),
        reply_markup=get_admin_panel_codes_kb()
    )


@router.callback_query(F.data.startswith('admin_codes_for_'))
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


@router.callback_query(F.data == 'add_code')
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


@router.message(GameCodeManagement.WaitingForTask)
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


@router.message(GameCodeManagement.WaitingForAnswer)
async def process_answer_input_handler(message: Message, state: FSMContext, game_task_repo: GameTaskRepository) -> None:
    answer = message.text
    if len(answer) < 1:
        await message.answer(
            text=_('⚠️ The length of a answer must be longer than one character!'),
            reply_markup=get_cancel_game_code_action_kb()
        )
        return

    data = await state.get_data()
    game_name: str = data['selected_game']
    task = data['task']

    new_code = await GameTaskService.create_task(
        game_name=game_name,
        task=task,
        answer=answer,
        game_task_repo=game_task_repo
    )
    await state.clear()
    await message.answer(
        text=_('✅ <i>Code for the game <b>{game}</b> successfully added!</i>\n\n'
               '🐥 <i>Task: <b>{task}</b></i>\n'
               '⛱️ <i>Answer: <b>{answer}</b></i>\n\n'
               'Select a game to add a new code or go back to the main menu:').format(
            game=new_code.game_name,
            task=new_code.task,
            answer=new_code.answer
        ),
        reply_markup=get_admin_panel_codes_kb()
    )


def register_admin_panel_game_codes_handlers(dp) -> None:
    dp.include_router(router)