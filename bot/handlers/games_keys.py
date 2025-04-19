import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common import ImageManager
from bot.common.static_data import HAMSTER_GAMES_LIST
from bot.handlers import PaginationCallbackData
from bot.keyboards.games_menu.games_menu import get_games_codes_and_keys_kb
from bot.keyboards.games_menu.pagination_kb import get_pagination_kb
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard
from infrastructure.db.repositories import UserRepository
from infrastructure.schemas import UserKeyGenerationSchema
from infrastructure.services import GameTaskService, PromoCodeService, UserService

games_keys_router = Router()
logger = logging.getLogger(__name__)


@games_keys_router.callback_query(F.data == 'get_games')
async def get_games_handler(callback_query: CallbackQuery, image_manager: ImageManager):
    """Display available games list with optional image."""
    user_id = callback_query.from_user.id
    logger.debug(f'User {user_id} requested games list')

    try:
        await callback_query.answer()
        await callback_query.message.delete()

        image = image_manager.get_random_image('handlers')
        response_text = _('📱 Select the game for which you want to get codes:')
        if image:
            await callback_query.message.answer_photo(
                photo=image, caption=response_text, reply_markup=get_games_codes_and_keys_kb()
            )
        else:
            logger.warning(f'No images available in game keys for user {user_id}')
            await callback_query.message.answer(text=response_text, reply_markup=get_games_codes_and_keys_kb())
    except Exception as e:
        logger.error(f'Games list error for {user_id}: {e}', exc_info=True)
        raise


@games_keys_router.callback_query(F.data.startswith('get_codes_for_'))
async def get_tasks_handler(callback_query: CallbackQuery, session: AsyncSession):
    """Initiate tasks pagination for selected game."""
    game_name = callback_query.data.split('_')[-1]
    logger.debug(f'User {callback_query.from_user.id} requested tasks for {game_name}')

    await process_tasks_page(callback_query=callback_query, session=session, game_name=game_name, current_page=1)


@games_keys_router.callback_query(PaginationCallbackData.filter())
async def handle_pagination(
    callback_query: CallbackQuery, callback_data: PaginationCallbackData, session: AsyncSession
):
    """Handle pagination navigation for tasks list."""
    game_name = callback_data.game_name
    current_page = callback_data.current_page
    logger.debug(f'User {callback_query.from_user.id} navigating page {current_page} for {game_name}')

    await process_tasks_page(
        callback_query=callback_query,
        session=session,
        game_name=game_name,
        current_page=current_page,
    )


async def process_tasks_page(callback_query: CallbackQuery, session: AsyncSession, game_name: str, current_page: int):
    """Process and display paginated tasks for a game."""
    user_id = callback_query.from_user.id

    try:
        response = await GameTaskService.get_paginated_response(session=session, game_name=game_name, page=current_page)

        if not response.tasks:
            logger.warning(f'No tasks found for {game_name}, page {current_page}')
            await callback_query.answer(text=_('No tasks/keys/codes available for this game.'), show_alert=True)
            return

        task_text = '\n'.join(
            [
                '<b>{task}</b> - <code>{answer}</code>'.format(task=task.task.strip(), answer=task.answer.strip())
                for task in response.tasks
            ]
        )

        logger.debug(f'Displaying {len(response.tasks)} tasks for {game_name} to {user_id}')
        await callback_query.message.edit_text(
            text=task_text + _('\n\n🔖 (<i>click to copy</i>)'),
            reply_markup=get_pagination_kb(
                current_page=response.page, total_pages=response.total_pages, game_name=game_name
            ),
        )
    except Exception as e:
        logger.error(f'Tasks processing error for {user_id}: {e}', exc_info=True)
        raise


@games_keys_router.callback_query(F.data == 'noop')
async def noop_handler(callback_query: CallbackQuery) -> None:
    """Handle empty callback (no operation)."""
    await callback_query.answer()


@games_keys_router.callback_query(F.data == 'hamster_keys')
async def get_hamster_keys(callback_query: CallbackQuery, session: AsyncSession) -> None:  # noqa C901
    """Generate and display hamster game promo codes."""
    user_id: int = callback_query.from_user.id
    logger.debug(f'Hamster keys request from user {user_id}')

    try:
        validation_result: UserKeyGenerationSchema = await UserService.get_hamster_keys_request_validation(
            session, user_id
        )
        if not validation_result.can_generate:
            if validation_result.daily_limit_exceeded:
                logger.info(f'Daily limit exceeded for user {user_id}')
                await callback_query.answer(text='🥹 You have reached your daily key limit.', show_alert=True)
                return
            if validation_result.remaining_time:
                logger.info(f'Cooldown active for user {user_id}')
                minutes = validation_result.remaining_time.minutes
                seconds = validation_result.remaining_time.seconds
                time_text = (
                    _('⏱️ Wait for {minutes} min {seconds} sec before getting the next key.').format(
                        minutes=minutes, seconds=seconds
                    )
                    if minutes
                    else _('⏱️ Wait for {seconds} sec before getting the next key.').format(seconds=seconds)
                )
                await callback_query.answer(time_text, show_alert=True)
                return

        logger.debug(f'Generating promo codes for user {user_id}')
        try:
            promo_codes = await PromoCodeService.consume_promo_codes(session, HAMSTER_GAMES_LIST)
            logger.info(f'Generated {len(promo_codes)} codes for user {user_id}')
        except Exception as e:
            logger.error(f'Promo code error for {user_id}: {e}', exc_info=True)
            await callback_query.answer(
                text=_('An error occurred while retrieving promo codes. Please try again later.'), show_alert=True
            )
            return
        text = []
        for game_name, promo_code in promo_codes.items():
            if promo_code:
                text.append(f'<b>{game_name}:</b>\n • <code>{promo_code}</code>\n')
            # ____________________________________
            # Removed to avoid showing extra lines.
            # ------------------------------------
            # else:
            #     text.append(_('<b>{}:</b>\n • <i>No promo codes available 🥹</i>').format(game_name))
        if not text:
            formatted_text = _('<i>No promo codes available 🥹</i>')
        else:
            formatted_text = '\n'.join(text)

        await UserRepository.update_user_activity(session, user_id)
        logger.debug(f'User activity updated for {user_id}')
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('{text}\n\n🔖 (click to copy)').format(text=formatted_text),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        logger.debug(f'Successfully sent codes to user {user_id}')
    except Exception as e:
        logger.error(f'Hamster keys error for {user_id}: {e}', exc_info=True)
        raise
