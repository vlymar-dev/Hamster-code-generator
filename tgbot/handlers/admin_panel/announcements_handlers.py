import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.announcement_repo import AnnouncementRepository
from infrastructure.repositories.user_repo import UserRepository
from tgbot.common.staticdata import LANGUAGES_DICT
from tgbot.keyboards.admin_panel.announcements_kb import (
    get_announcement_menu_kb,
    get_announcements_kb,
    get_announcements_languages_kb,
    get_back_to_announcements_kb,
    get_cancel_announcement_action_kb,
)
from tgbot.services.admin_panel.announcements_service import AnnouncementService
from tgbot.states.announcements_state import DeleteAnnouncement, AnnouncementDetails, CreateAnnouncement

logger = logging.getLogger(__name__)

router = Router()


async def show_announcements_text(announcement_repo: AnnouncementRepository) -> str:
    announcements = await AnnouncementService.show_announcements_with_languages(announcement_repo)

    if announcements:
        posts = "\n\n".join(
            [
                f'🔅 <b>ID:</b> <code>{announcement["id"]}</code>\n'
                f'🔖 <b>Title:</b> {announcement["title"]}\n'
                f'🌏 <b>Languages:</b> {", ".join(announcement["languages"]) if announcement["languages"] else _("No translations available")}'
                for announcement in announcements
            ]
        )
        return _('📌 All announcements:\n\n') + posts
    else:
        return _('No announcements yet.')


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
    await state.set_state(CreateAnnouncement.Title)


@router.message(CreateAnnouncement.Title)
async def process_announcement_text_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(Title=message.html_text)
    await state.set_state(CreateAnnouncement.Image)
    await message.answer(
        text=_('📝 <b>Title:</b>\n{title}\n\n'
               'Send an image or type <code>no_image</code> to skip.').format(title=message.html_text),
        reply_markup=get_cancel_announcement_action_kb()
    )



@router.message(CreateAnnouncement.Image)
async def process_announcement_image_handler(message: Message, state: FSMContext, announcement_repo: AnnouncementRepository, bot: Bot) -> None:
    data = await state.get_data()

    if message.photo:
        try:
            photo = message.photo[-1]
            image_url = await AnnouncementService.process_and_save_image(photo, bot)
            announcement = await AnnouncementService.create_announcement_without_text_translation(
                title=data['Title'],
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
            title=data['Title'],
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


@router.callback_query(F.data == 'view_announcement_detail')
async def view_announcement_detail_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement id:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(AnnouncementDetails.ID)


@router.message(AnnouncementDetails.ID)
async def process_announcement_id_input(message: Message, state: FSMContext, announcement_repo: AnnouncementRepository) -> None:
    try:
        announcement_id = int(message.text)
        title, english_text, language_codes, image_url = await AnnouncementService.get_announcement_details(
            announcement_id, announcement_repo
        )

        await state.update_data(announcement_id=message.text)
        await state.update_data(Languages=language_codes)

        text = _('🔖 <b>Title:</b> {title}\n\n'
                 '🌏 <b>Languages:</b> {languages}\n\n'
                 '📙 <b>Text:</b> {text}'
                 ).format(
                    title=title,
                    languages=", ".join(language_codes),
                    text=english_text or _("No text available."),
                )
        if image_url:
            await message.answer_photo(
                photo=FSInputFile(image_url),
                caption=text,
                reply_markup=get_announcement_menu_kb()
            )
        else:
            await message.answer(
                text=text,
                reply_markup=get_announcement_menu_kb()
            )
    except ValueError as e:
        await message.answer(
            text=_('⚠️ {error}').format(error=str(e)),
            reply_markup=get_cancel_announcement_action_kb()
        )
    except Exception as e:
        await message.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_cancel_announcement_action_kb()
        )
        logger.error(f"Error in process_announcement_id_input: {e}")


@router.callback_query(F.data == 'create_announcement_translation')
async def create_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text_languages = data['Languages']
    available_languages_dict = AnnouncementService.get_available_languages(
        languages=LANGUAGES_DICT,
        text_languages=text_languages,
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('🌏 Select a language from the list of available languages:'),
        reply_markup=get_announcements_languages_kb(available_languages_dict)
    )


@router.callback_query(F.data.startswith('announcement_text_'))
async def get_announcement_text_language_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    language_code: str = callback_query.data.split('_')[-1]
    await state.update_data(LanguageCode=language_code)
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement text for {language_code}:').format(language_code=language_code),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(AnnouncementDetails.TranslationText)


@router.message(AnnouncementDetails.TranslationText)
async def process_translation_text_input(message: Message, state: FSMContext, announcement_repo: AnnouncementRepository) -> None:
    data = await state.get_data()
    announcement_id = int(data['announcement_id'])
    language_code = data['LanguageCode']
    translation_text = message.html_text

    try:
        translation_text = await AnnouncementService.create_translation_for_announcement(
            announcement_id=announcement_id,
            language_code=language_code,
            text=translation_text,
            announcement_repo=announcement_repo,
        )
        await message.answer(
            text=_('✅ Translation for: \'{language}\' created').format(
                language=translation_text.language_code
            ),
            reply_markup=get_back_to_announcements_kb()
        )
    except ValueError as e:
        await message.answer(
            text=_('❌ {error}').format(error=str(e)),
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
async def delete_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement id to delete:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(DeleteAnnouncement.ID)



@router.message(DeleteAnnouncement.ID)
async def process_delete_announcement_handler(message: Message, announcement_repo: AnnouncementRepository, state: FSMContext) -> None:
    try:
        announcement_id = int(message.text)

        await AnnouncementService.delete_announcement(announcement_id, announcement_repo)
        await state.clear()
        await message.answer(
            text=_('✅ Announcement with ID: <b>{id}</b> has been deleted.').format(id=announcement_id),
            reply_markup=get_back_to_announcements_kb()
        )
    except ValueError as e:
        await message.answer(
            text=_('❌ {error}').format(error=str(e)),
            reply_markup=get_back_to_announcements_kb()
        )
    except Exception as e:
        await state.clear()
        await message.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_back_to_announcements_kb()
        )
        logger.error(f"Error in delete_announcement_handler: {e}")


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