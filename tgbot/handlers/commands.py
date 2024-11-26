from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from infrastructure.models.user import User
from infrastructure.repositories.referral_repo import ReferralRepository
from infrastructure.repositories.user_repo import UserRepository
from tgbot.filters.admin_filter import AdminFilter
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb
from tgbot.keyboards.settings.change_language_kb import get_change_language_kb
from tgbot.services.admin_panel.admin_panel_service import AdminPanelService

router = Router()


@router.message(CommandStart())
async def handle_start_command(message: Message, user_repo: UserRepository, bot: Bot, referral_repo: ReferralRepository) -> None:
    user: bool = await user_repo.check_user_exists(message.from_user.id)
    if not user:
        new_user = User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )
        await user_repo.add_user(new_user)

        args = message.text.split(maxsplit=1)
        if len(args) > 1 and args[1].isdigit():
            referrer_id = int(args[1])
            referrer_exists = await user_repo.check_user_exists(referrer_id)
            if referrer_exists:
                await referral_repo.add_referral(referrer_id=referrer_id, referred_id=message.from_user.id)
                referrer_message = _(
                            f"🎉 User with ID <b>{message.from_user.id}</b> registered using your referral link!"
                        )
                await bot.send_message(referrer_id, referrer_message)
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


@router.message(Command('change_language'))
async def change_language_command(message: Message):
    await message.answer(text=_('Please choose a language:'), reply_markup= get_change_language_kb())


@router.message(Command('paysupport'))
async def paysupport_command(message: Message) -> None:
    await message.delete()
    await message.answer(
        text=_('💡 <b>Your donation helps us make the bot better and add exciting new features!\n'
               'Thank you for supporting us!💪</b>\n'
               '<i>Please note that donations are voluntary and non-refundable.</i>\n'
               'If you have any questions, contact us. 📞'),
        reply_markup=get_back_to_main_menu_keyboard()
    )


@router.message(Command('admin'), AdminFilter())
async def admin_command(message: Message) -> None:
    await AdminPanelService.show_admin_panel(message)


def register_commands_handler(dp) -> None:
    dp.include_router(router)
