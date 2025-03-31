from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from humanfriendly.terminal import message

from bot.handlers.callback_data import PaginationCallbackData
from bot.handlers.main_menu import send_main_menu
from bot.keyboards.games_menu.games_menu import get_games_codes_and_keys_kb
from bot.keyboards.games_menu.pagination_kb import get_pagination_kb
from bot.services.game_task_service import GameTaskService
from infrastructure.repositories.game_task_repo import GameTaskRepository

games_keys_router = Router()


@games_keys_router.callback_query(F.data == 'get_games')
async def get_games_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=_('📱 Select the game for which you want to get codes:'),
        reply_markup=get_games_codes_and_keys_kb()
    )


@games_keys_router.callback_query(F.data.startswith('get_codes_for_'))
async def get_tasks_handler(callback_query: CallbackQuery, game_task_repo: GameTaskRepository):
    game_name = callback_query.data.split('_')[-1]

    await process_tasks_page(
        game_task_repo=game_task_repo,
        callback_query=callback_query,
        game_name=game_name,
        current_page=1
    )


@games_keys_router.callback_query(PaginationCallbackData.filter())
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


@games_keys_router.callback_query(F.data == 'noop')
async def noop_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()


@games_keys_router.callback_query(F.data == 'hamster_keys')
async def get_hamster_keys(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await send_main_menu(callback_query)
    # user_id: int = callback_query.from_user.id
    #
    # validation_result = await UserKeyService.validate_user_request(user_id, user_key_repo)
    # if not validation_result['can_generate']:
    #     if validation_result['reason'] == 'daily_limit_exceeded':
    #         await callback_query.answer(
    #             text='🥹 You have reached your daily key limit.',
    #             show_alert=True
    #         )
    #         return
    #     elif validation_result['reason'] == 'interval_not_met':
    #         remaining_time = validation_result['remaining_time']
    #         minutes = remaining_time.get('min')
    #         seconds = remaining_time.get('sec')
    #         if minutes:
    #             time_text = _('⏱️ Wait for {minutes} min {seconds} sec before getting the next key.').format(
    #                 minutes=minutes, seconds=seconds
    #             )
    #         else:
    #             time_text = _('⏱️ Wait for {seconds} sec before getting the next key.').format(seconds=seconds)
    #         await callback_query.answer(time_text, show_alert=True)
    #         return
    #
    # try:
    #     promo_codes = await PromoCodeService.get_and_delete_promo_codes(
    #         game_names=HAMSTER_GAMES_LIST,
    #         user_id=user_id,
    #         promo_code_repo=promo_code_repo,
    #         user_key_repo=user_key_repo)
    # except Exception as e:
    #     logger.error(f'Error during promo code retrieval for user_id={user_id}: {e}')
    #     await callback_query.answer(
    #         text=_('An error occurred while retrieving promo codes. Please try again later.'),
    #         show_alert=True
    #     )
    #     return
    # text = []
    # for game_name, promo_code in promo_codes.items():
    #     if promo_code:
    #         text.append(f'<b>{game_name}:</b>\n • <code>{promo_code}</code>\n')
    #     else:
    #         text.append(_('<b>{}:</b>\n • <i>No promo codes available 🥹</i>').format(game_name))
    #
    # formatted_text = '\n'.join(text)
    # await UserKeyService.update_user_activity(user_id, user_key_repo)
    # await callback_query.answer()
    # await callback_query.message.delete()
    # await callback_query.message.answer(
    #     text=_('{text}\n\n🔖 (click to copy)').format(text=formatted_text),
    #     reply_markup=get_back_to_main_menu_keyboard()
    # )