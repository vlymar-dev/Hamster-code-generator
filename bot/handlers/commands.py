from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters import AdminFilter
from bot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb
from bot.keyboards.settings.change_language_kb import get_change_language_kb
from bot.services.admin_panel.admin_panel_service import AdminPanelService
from core.shemas.referral import ReferralCreateSchema
from core.shemas.user import UserCreateSchema
from db.repositories import ReferralsRepository, UserRepository

commands_router = Router()


@commands_router.message(CommandStart())
async def handle_start_command(message: Message, session: AsyncSession, bot: Bot) -> None:
    user_id: int = message.from_user.id
    exists_user: bool = await UserRepository.check_user_exists(session, user_id)
    if not exists_user:
        user: UserCreateSchema = UserCreateSchema(
            id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )
        await UserRepository.add_user(session, user)

        try:
            # Adding a referral
            args = message.text.split(maxsplit=1)
            referrer_id = int(args[1])
            exists_referrer: bool = await UserRepository.check_user_exists(session, referrer_id)
            if len(args) > 1 and args[1].isdigit() and exists_referrer:
                referrals_data = ReferralCreateSchema(
                    referrer_id=referrer_id,
                    referred_id=user_id
                )
                await ReferralsRepository.add_referral(session, referrals_data)
                referrer_message = _(
                            f'🎉 User {message.from_user.full_name} with ID <b>{message.from_user.id}</b> '
                            f'registered using your referral link!'
                        )
                await bot.send_message(referrer_id, referrer_message)
        except Exception:
            ...

    await message.answer(
        text=_('👋 Hello, <b>{first_name}</b>!\n'
               '🛳️ <i>Welcome aboard!</i>\n\n'
               '🌊 Join the adventure with us — pick an action below and start playing! 🚀 \n'
               '🎈 Here you’ll find <i>exclusive growth opportunities</i> and bonuses for active players.\n'
               '🏆 Play, progress, and unlock new rewards with every step! \n\n'
               '📖 <i>Terms of use are available in the <b>Info</b> section.</i>').format(
            first_name=message.from_user.first_name,
        ),
        reply_markup=get_main_menu_kb()
    )


@commands_router.message(Command('change_language'))
async def change_language_command(message: Message, session: AsyncSession):
    current_language_code: str = await UserRepository.get_user_language(session, message.from_user.id)

    await message.answer(text=_('Please choose a language:'), reply_markup= get_change_language_kb(current_language_code))


@commands_router.message(Command('paysupport'))
async def paysupport_command(message: Message) -> None:
    await message.delete()
    await message.answer(
        text=_('💡 <b>Your donation helps us make the bot better and add exciting new features!\n'
               'Thank you for supporting us!💪</b>\n'
               '<i>Please note that donations are voluntary and non-refundable.</i>\n'
               'If you have any questions, contact us. 📞'),
        reply_markup=get_back_to_main_menu_keyboard()
    )


@commands_router.message(Command('admin'), AdminFilter())
async def admin_command(message: Message) -> None:
    await AdminPanelService.show_admin_panel(message)
