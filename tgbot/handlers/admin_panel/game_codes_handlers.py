from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from tgbot.keyboards.admin_panel.game_codes_kb import (
    get_admin_panel_codes_kb,
    get_cancel_game_code_action_kb,
    get_game_codes_actions_kb,
)
from tgbot.states.game_code_state import AddGameCode

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
    await state.update_data(GameName=game_name)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('<b>Select an action:</b>'),
        reply_markup=get_game_codes_actions_kb()
    )


@router.callback_query(F.data == 'add_code')
async def add_game_code_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddGameCode.Question)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('🐥 Enter a question for the game:'),
        reply_markup=get_cancel_game_code_action_kb()
    )


@router.message(AddGameCode.Question)
async def process_add_game_task_handler(message: Message, state: FSMContext) -> None:
    if len(message.text) < 1:
        await message.answer(
            text=_('⚠️ The length of a question must be longer than one character!'),
            reply_markup=get_cancel_game_code_action_kb()
        )
        return
    await state.update_data(Question=message.text)
    await state.set_state(AddGameCode.Answer)
    await message.answer(
        text=_('⛱️ Enter an answer for the game:'),
        reply_markup=get_cancel_game_code_action_kb()
    )


@router.message(AddGameCode.Answer)
async def process_add_game_answer_handler(message: Message, state: FSMContext) -> None:
    if len(message.text) < 1:
        await message.answer(
            text=_('⚠️ The length of a answer must be longer than one character!'),
            reply_markup=get_cancel_game_code_action_kb()
        )
        return
    data = await state.get_data()
    game_name: str = data['GameName']
    question: str = data['Question']
    answer: str = message.text
    await state.clear()
    await message.answer(
        text=_('{game_name}, {question}, {answer}'
               '\n'
               'Select a game to add a new code or go back to the main menu:').format(game_name=game_name, question=question, answer=answer),
        reply_markup=get_admin_panel_codes_kb()
    )


def register_admin_panel_game_codes_handlers(dp) -> None:
    dp.include_router(router)