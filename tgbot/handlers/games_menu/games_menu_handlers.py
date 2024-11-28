import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.game_task_repo import GameTaskRepository
from tgbot.handlers.callback_data import PaginationCallbackData
from tgbot.keyboards.games_menu.games_menu import get_games_codes_and_keys_kb
from tgbot.keyboards.games_menu.pagination_kb import get_pagination_kb
from tgbot.services.game_task_service import GameTaskService

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'get_games')
async def get_games_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('📱 Select the game for which you want to get codes:'),
        reply_markup=get_games_codes_and_keys_kb()
    )


@router.callback_query(F.data.startswith('get_codes_for_'))
async def get_tasks_handler(callback_query: CallbackQuery, game_task_repo: GameTaskRepository):
    game_name = callback_query.data.split('_')[-1]

    await process_tasks_page(
        game_task_repo=game_task_repo,
        callback_query=callback_query,
        game_name=game_name,
        current_page=1
    )


@router.callback_query(PaginationCallbackData.filter())
async def handle_pagination(
    callback_query: CallbackQuery,
    callback_data: PaginationCallbackData,
    game_task_repo: GameTaskRepository
):
    game_name = callback_data.game_name
    current_page = callback_data.current_page

    await process_tasks_page(
        callback_query=callback_query,
        game_name=game_name,
        current_page=current_page,
        game_task_repo=game_task_repo
    )


async def process_tasks_page(
    callback_query: CallbackQuery,
    game_name: str,
    current_page: int,
    game_task_repo: GameTaskRepository
):
    tasks, page, total_pages = await GameTaskService.get_paginated_response(
        game_task_repo=game_task_repo,
        game_name=game_name,
        page=current_page
    )

    if not tasks:
        await callback_query.answer(
            text=_('No tasks/keys/codes available for this game.'),
            show_alert=True
        )
        return

    task_text = '\n'.join(['<b>{task}</b> - <code>{answer}</code>'.format(task=task.task.strip(), answer=task.answer.strip()) for task in tasks])
    pagination_keyboard = get_pagination_kb(
        current_page=page,
        total_pages=total_pages,
        game_name=game_name
    )

    await callback_query.message.edit_text(
        text=task_text + _('\n\n🔖 (<i>click to copy</i>)'),
        reply_markup=pagination_keyboard
    )


@router.callback_query(F.data == 'noop')
async def noop_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()


def register_games_menu_handler(dp) -> None:
    dp.include_router(router)
