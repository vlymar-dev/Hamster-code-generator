from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.exceptions.exceptions import SelfReferralException, UserAlreadyExistsException
from tgbot.keyboards.change_language_kb import get_change_language_kb
from tgbot.keyboards.main_menu_kb import get_back_to_main_menu_keyboard, get_main_menu_kb

router = Router()


@router.message(CommandStart())
async def handle_start_command(message: Message, db: Database) -> None:
    args = message.text.split(maxsplit=1)
    welcome_message = _('👋 Hello, <b>{first_name}</b>!\n'
                   '🛳️ <i>Welcome aboard!</i>\n\n'
                   '🌊 Join the adventure with us — pick an action below and start playing! 🚀 \n'
                   '🎈 Here you’ll find <i>exclusive growth opportunities</i> and bonuses for active players.\n'
                   '🏆 Play, progress, and unlock new rewards with every step! \n\n'
                   '📖 <i>Terms of use are available in the <b>Info</b> section.</i>').format(
                first_name=message.from_user.first_name,
            )
    if len(args) > 1 and args[1].isdigit():
        try:
            referrer_id = int(args[1])
            await db.add_referral(user_id=message.from_user.id, referral_id=referrer_id)
            referrer_message=_(
                '🎉 You’ve joined through the referral link of user ID <b>{referrer_id}</b>!\n\n'
            ).format(
                referrer_id=referrer_id
            )
            await message.answer(
                text=referrer_message + welcome_message,
                reply_markup=get_main_menu_kb()
            )
        except SelfReferralException:
                await message.answer(text=_(
                    'Oops! 🚫 You can’t use your own referral link!'
                ))
        except UserAlreadyExistsException:
            await message.answer(
                text=welcome_message,
                reply_markup=get_main_menu_kb()
            )
    else:
        await message.answer(
            text=welcome_message,
            reply_markup=get_main_menu_kb()
        )
    user = message.from_user
    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'language_code': user.language_code,
    }
    await db.add_user(user_data)


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


def register_commands_handler(dp) -> None:
    dp.include_router(router)
