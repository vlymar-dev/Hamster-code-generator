from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.announcement_repo import AnnouncementRepository
from infrastructure.repositories.user_repo import UserRepository
from tgbot.keyboards.admin_panel.announcements_kb import (
    get_announcements_kb,
    get_back_to_announcements_kb,
    get_cancel_announcement_action_kb,
)
from tgbot.services.admin_panel.announcements_service import AnnouncementService
from tgbot.states.announcements_state import CreateAnnouncementState

router = Router()


async def show_announcements_text(announcement_repo: AnnouncementRepository) -> str:
    announcements = await AnnouncementService.show_announcements(announcement_repo)

    if announcements:
        posts = "\n\n".join(
            [f"🔖 ID: <code>{announcement.id}</code>\n{announcement.title}" for announcement in announcements]
        )
        return _("📌 All announcements:\n\n") + posts
    else:
        return _("No announcements yet.")


@router.callback_query(F.data == 'manage_announcements')
async def manage_announcements_handler(callback_query: CallbackQuery, announcement_repo: AnnouncementRepository) -> None:
    text = await show_announcements_text(announcement_repo)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_announcements_kb()
    )


@router.callback_query(F.data == 'create_announcement')
async def create_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement title:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(CreateAnnouncementState.announcement_title)


@router.message(CreateAnnouncementState.announcement_title)
async def process_announcement_text_handler(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(announcement_title=message.html_text)
        await state.set_state(CreateAnnouncementState.announcement_image)
        await message.answer(
            text=_('📝 Text:\n{text}\n\n'
                   'Send an image or type <code>no_image</code> to skip.').format(text=message.html_text),
            reply_markup=get_cancel_announcement_action_kb()
        )



@router.message(CreateAnnouncementState.announcement_image)
async def process_announcement_image_handler(message: Message, state: FSMContext, announcement_repo: AnnouncementRepository, bot: Bot) -> None:
    data = await state.get_data()

    if message.photo:
        try:
            photo = message.photo[-1]
            image_url = await AnnouncementService.process_and_save_image(photo, bot)
            announcement = await AnnouncementService.create_announcement_without_text_translation(
                title=data['announcement_title'],
                created_by=message.from_user.id,
                image_url=image_url,
                announcement_repo=announcement_repo
            )
            await state.clear()
            await message.answer(
                text=_('✅ Announcement "{title}" with image created.').format(title=announcement.title),
                reply_markup=get_back_to_announcements_kb()
            )
        except ValueError as e:
            await message.answer(
                text=_('🚫 Unsupported image format. Please send a correct image.'),
                reply_markup=get_cancel_announcement_action_kb()
            )

    elif message.text.lower().strip() in ['no_image']:
        announcement = await AnnouncementService.create_announcement_without_text_translation(
            title=data['announcement_title'],
            created_by=message.from_user.id,
            announcement_repo=announcement_repo
        )
        await state.clear()
        await message.answer(
            text=_('✅ Announcement "{title}" without image created.').format(title=announcement.title),
            reply_markup=get_back_to_announcements_kb()
        )
    else:
        await message.answer(
            text=_('Please submit an image or enter <code>no_image</code> to skip.'),
            reply_markup=get_cancel_announcement_action_kb()
        )


@router.callback_query(F.data == 'edit_announcement')
async def edit_announcement_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()


@router.callback_query(F.data == 'view_announcements')
async def view_announcements_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()



@router.callback_query(F.data == 'delete_announcement')
async def delete_announcement_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()



@router.callback_query(F.data == 'broadcast_announcement')
async def broadcast_announcement_handler(callback_query: CallbackQuery, user_repo: UserRepository) -> None:
    await callback_query.message.delete()
    await callback_query.answer()



@router.callback_query(F.data == 'back_to_announcements')
async def back_to_announcements_handler(callback_query: CallbackQuery, state: FSMContext, announcement_repo: AnnouncementRepository) -> None:
    text = await show_announcements_text(announcement_repo)
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_announcements_kb()
    )


def register_announcements_handlers(dp) -> None:
    dp.include_router(router)