import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common import ImageManager
from bot.filters import AdminFilter, IsBannedFilter
from bot.handlers.admin_panel import show_admin_panel
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb
from bot.keyboards.settings.change_language_kb import get_change_language_kb
from infrastructure.schemas.user import UserCreateSchema
from infrastructure.services import CacheService, UserCacheService, UserService

logger = logging.getLogger(__name__)
commands_router = Router()


@commands_router.message(CommandStart())
async def handle_start_command(message: Message, session: AsyncSession, bot: Bot, image_manager: ImageManager) -> None:
    """Handle /start command with referral system and welcome message."""
    logger.info(f'Processing /start command from user {message.from_user.id}')

    try:
        user_id: int = message.from_user.id
        logger.debug(f'Parsing referral ID for user {user_id}')
        n, n, ref_id = message.text.partition(' ')
        referrer_id = int(ref_id) if ref_id.isdigit() and int(ref_id) != user_id else None

        user_data: UserCreateSchema = UserCreateSchema(
            id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )
        logger.debug(f'Registering user {user_id}')
        new_user = await UserService.user_registration(session=session, user_id=user_id, user_data=user_data)

        if new_user and referrer_id:
            logger.info(f'Processing referral for user {user_id} from referrer {referrer_id}')
            success = await UserService.referral_adding(session=session, referrer_id=referrer_id, referred_id=user_id)
            if success:
                logger.debug(f'Sending referral notification to {referrer_id}')
                await bot.send_message(
                    chat_id=referrer_id,
                    text=_('🎉 User {full_name} with ID <b>{user_id}</b> registered using your referral link!').format(
                        full_name=message.from_user.full_name, user_id=message.from_user.id
                    ),
                )
        image = image_manager.get_random_image('handlers')
        response_text = _(
            '👋 Hello, <b>{first_name}</b>!\n'
            '🛳️ <i>Welcome aboard!</i>\n\n'
            '🌊 Join the adventure with us — pick an action below and start playing! 🚀 \n'
            '🎈 Here you’ll find <i>exclusive growth opportunities</i> and bonuses for active players.\n'
            '🏆 Play, progress, and unlock new rewards with every step! \n\n'
            '📖 <i>Terms of use are available in the <b>Info</b> section.</i>'
        )

        if image:
            await message.answer_photo(
                photo=image,
                caption=response_text.format(first_name=message.from_user.first_name),
                reply_markup=get_main_menu_kb(),
            )
        else:
            logger.warning(f'No images available in /start for user {user_id}')
            await message.answer(
                text=response_text.format(first_name=message.from_user.first_name), reply_markup=get_main_menu_kb()
            )
    except Exception as e:
        logger.error(f'Error processing /start for user {message.from_user.id}: {e}', exc_info=True)
        raise


@commands_router.message(Command('change_language'))
async def change_language_command(message: Message, session: AsyncSession, cache_service: CacheService):
    """Handle language change command."""
    logger.debug(f'Language change request from user {message.from_user.id}')

    try:
        user_id = message.from_user.id
        logger.debug(f'Fetching current language for user {user_id}')
        language_data = await UserCacheService.get_user_language(
            cache_service=cache_service, session=session, user_id=user_id
        )
        current_language_code = language_data.language_code
        logger.debug(f'Current language: {current_language_code} for user {user_id}')
        await message.answer(
            text=_('Please choose a language:'), reply_markup=get_change_language_kb(current_language_code)
        )
    except Exception as e:
        logger.error(f'Language change error for user {message.from_user.id}: {e}', exc_info=True)
        raise


@commands_router.message(Command('paysupport'), IsBannedFilter())
async def paysupport_command(message: Message) -> None:
    """Handle donation information command."""
    logger.debug(f'Paysupport command from user {message.from_user.id}')

    try:
        await message.delete()
        await message.answer(
            text=_(
                '💡 <b>Your donation helps us make the bot better and add exciting new features!\n'
                'Thank you for supporting us!💪</b>\n'
                '<i>Please note that donations are voluntary and non-refundable.</i>\n'
                'If you have any questions, contact us. 📞'
            ),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    except Exception as e:
        logger.error(f'Paysupport command error: {e}', exc_info=True)
        raise


@commands_router.message(Command('admin'), IsBannedFilter(), AdminFilter())
async def admin_command(message: Message) -> None:
    """Handle admin panel access."""
    logger.debug(f'Admin access request from user {message.from_user.id}')
    try:
        await show_admin_panel(message)
        logger.info(f'Admin panel displayed for user {message.from_user.id}')
    except Exception as e:
        logger.error(f'Admin command error: {e}', exc_info=True)
        raise
