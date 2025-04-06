import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.static_data import LANGUAGES_DICT
from bot.keyboards.admin_panel.announcements_kb import (
    get_announcement_menu_kb,
    get_announcements_kb,
    get_back_to_announcement_details_kb,
    get_back_to_announcements_kb,
    get_cancel_announcement_action_kb,
    get_confirmation_broadcast_kb,
    get_languages_kb,
)
from bot.states import AnnouncementDetails, CreateAnnouncement, DeleteAnnouncement
from core.schemas import AnnouncementCreateSchema, AnnouncementTranslationCreateSchema
from core.services import AdminPanelService
from db.repositories import AnnouncementRepository

logger = logging.getLogger(__name__)

announcements_router = Router()


@announcements_router.callback_query(F.data == 'manage_announcements')
async def manage_announcements_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    text = await show_announcements_text(session)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_announcements_kb()
    )


@announcements_router.callback_query(F.data == 'create_announcement')
async def create_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement title:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(CreateAnnouncement.title)


@announcements_router.message(CreateAnnouncement.title)
async def process_announcement_title_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.html_text)
    await state.set_state(CreateAnnouncement.image)
    await message.answer(
        text=_('📝 <b>Title:</b>\n{title}\n\n'
               'Send an image or type <code>no_image</code> to skip.').format(title=message.html_text),
        reply_markup=get_cancel_announcement_action_kb()
    )


@announcements_router.message(CreateAnnouncement.image)
async def process_announcement_image_handler(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    data = await state.get_data()

    if message.photo:
        try:
            photo = message.photo[-1]
            image_url = await AdminPanelService.process_and_save_image(photo, bot)
            data = AnnouncementCreateSchema(
                    title=data['title'],
                    created_by=message.from_user.id,
                    image_url=image_url
                )
            await AnnouncementRepository.add_announcement(session, data)
            await message.answer(
                text=_('✅ Announcement "{title}" with image created.').format(title=data.title),
                reply_markup=get_back_to_announcements_kb()
            )
        except ValueError:
            await message.answer(
                text=_('🚫 Unsupported image format. Please send a correct image.'),
                reply_markup=get_cancel_announcement_action_kb()
            )

    elif message.text.lower().strip() in ['no_image']:
        data = AnnouncementCreateSchema(
            title=data['title'],
            created_by=message.from_user.id
        )
        await AnnouncementRepository.add_announcement(session, data)

        await message.answer(
            text=_('✅ Announcement "{title}" without image created.').format(title=data.title),
            reply_markup=get_back_to_announcements_kb()
        )
    else:
        await message.answer(
            text=_('Please submit an image or enter <code>no_image</code> to skip.'),
            reply_markup=get_cancel_announcement_action_kb()
        )
    await state.clear()


@announcements_router.callback_query(F.data == 'view_announcement_detail')
async def view_announcement_detail_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement id:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(AnnouncementDetails.id)


@announcements_router.message(AnnouncementDetails.id)
async def process_announcement_id_input(message: Message, state: FSMContext, session: AsyncSession) -> None:
    try:
        announcement_id = int(message.text)

        await show_announcement_details(
            target=message,
            announcement_id=announcement_id,
            session=session,
            state=state
        )
    except ValueError as e:
        await message.answer(
            text=_('⚠️ {error}').format(error=str(e)),
            reply_markup=get_cancel_announcement_action_kb()
        )


@announcements_router.callback_query(F.data == 'create_announcement_translation')
async def create_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    available_languages = {key: value for key, value in LANGUAGES_DICT.items() if key not in data['languages']}
    await callback_query.message.delete()
    await callback_query.answer()
    if available_languages:
        await callback_query.message.answer(
            text=_('🌏 Select a language from the available languages:'),
            reply_markup=get_languages_kb(available_languages, 'add_translation_text_')
        )
        return
    await callback_query.message.answer(
        text=_('⚠️ No available languages.'),
        reply_markup=get_back_to_announcement_details_kb()
    )


@announcements_router.callback_query(F.data.startswith('add_translation_text_'))
async def get_add_translation_text_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    language_code: str = callback_query.data.split('_')[-1]
    await state.update_data(language_code=language_code)
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement text for "{language_code}":').format(
            language_code=LANGUAGES_DICT.get(language_code)
        ),
        reply_markup=get_back_to_announcement_details_kb()
    )
    await state.set_state(AnnouncementDetails.translation_text)


@announcements_router.message(AnnouncementDetails.translation_text)
async def process_translation_text_input(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    language_code = data['language_code']

    try:
        await AnnouncementRepository.add_translation_by_announcement_id(
            session=session,
            translation=AnnouncementTranslationCreateSchema(
                announcement_id=int(data['id']),
                text=message.html_text,
                language_code=language_code
            )
        )
        await message.answer(
            text=_('✅ Translation for: \'{language}\' created').format(
                language=LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb()
        )
        data.pop('language_code', None)
        await state.update_data(**data)
    except ValueError as e:
        await message.answer(
            text=_('❌ {error}').format(error=str(e)),
            reply_markup=get_back_to_announcement_details_kb()
        )


@announcements_router.callback_query(F.data == 'edit_announcement_translation')
async def edit_announcement_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    available_languages = {key: value for key, value in LANGUAGES_DICT.items() if key in data['languages']}

    await callback_query.message.delete()
    await callback_query.answer()
    if available_languages:
        await callback_query.message.answer(
            text=_('🌏 Select the language available for editing:'),
            reply_markup=get_languages_kb(available_languages, 'edit_translation_text_')
        )
        return
    await callback_query.message.answer(
        text=_('⚠️ No available translations for editing.'),
        reply_markup=get_back_to_announcement_details_kb()
    )

@announcements_router.callback_query(F.data.startswith('edit_translation_text_'))
async def get_edit_translation_text_handler(
        callback_query: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
) -> None:
    language_code: str = callback_query.data.split('_')[-1]
    data = await state.get_data()

    text = await AnnouncementRepository.get_translation_by_language_code(
        session=session,
        announcement_id=int(data['id']),
        language_code=language_code
    )
    await state.update_data(language_code=language_code)
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📙 <b>Text: </b>\n')
             + f'{text.text}\n\n'
             + _('📝 Enter new announcement text for "{language_code}":').format(
            language_code=LANGUAGES_DICT.get(language_code)),
        reply_markup=get_back_to_announcement_details_kb()
    )
    await state.set_state(AnnouncementDetails.edit_translation_text)


@announcements_router.message(AnnouncementDetails.edit_translation_text)
async def process_edit_translation_text_input(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    language_code = data['language_code']

    try:
        await AnnouncementRepository.update_translation(
            session=session,
            translation=AnnouncementTranslationCreateSchema(
                announcement_id=int(data['id']),
                text=message.html_text,
                language_code=language_code
            )
        )

        await message.answer(
            text=_('✅ Translation updated <b>successfully</b> for: \'{language}\'.').format(
                language=LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb()
        )
        data.pop('language_code', None)
        await state.update_data(**data)
    except ValueError as e:
        await message.answer(
            text=_('❌ {error}').format(error=str(e)),
            reply_markup=get_back_to_announcement_details_kb()
        )


@announcements_router.callback_query(F.data == 'delete_announcement')
async def delete_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('📝 Enter the announcement id to delete:'),
        reply_markup=get_cancel_announcement_action_kb()
    )
    await state.set_state(DeleteAnnouncement.id)


@announcements_router.message(DeleteAnnouncement.id)
async def process_delete_announcement_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
    try:
        announcement_id = int(message.text)
        await AnnouncementRepository.delete_announcement_by_id(session, announcement_id)
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
        logger.error(f'Error in delete_announcement_handler: {e}')


@announcements_router.callback_query(F.data == 'view_announcement_translation')
async def view_announcement_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    languages_dict = {key: value for key, value in LANGUAGES_DICT.items() if key in data['languages']}
    await callback_query.message.delete()
    await callback_query.answer()
    if languages_dict:
        await callback_query.message.answer(
            text=_('🌏 Select a language from the list of available languages:'),
            reply_markup=get_languages_kb(languages_dict, 'view_translation_text_')
        )
        return
    await callback_query.message.answer(
        text=_('⚠️ No available translations to view.'),
        reply_markup=get_back_to_announcement_details_kb()
    )

@announcements_router.callback_query(F.data.startswith('view_translation_text_'))
async def get_view_translation_text_handler(
        callback_query: CallbackQuery,
        session: AsyncSession,
        state: FSMContext
) -> None:
    data = await state.get_data()
    text = await AnnouncementRepository.get_translation_by_language_code(
        session=session,
        announcement_id=int(data['id']),
        language_code=callback_query.data.split('_')[-1]
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=text.text,
        reply_markup=get_back_to_announcement_details_kb()
    )


@announcements_router.callback_query(F.data == 'broadcast_announcement')
async def broadcast_announcement_request_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=_('🫔 Are you sure you want to broadcast this announcement?'),
        reply_markup=get_confirmation_broadcast_kb()
    )


@announcements_router.callback_query(F.data == 'confirm_broadcast')
async def confirm_broadcast_handler(
        callback_query: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        bot: Bot
) -> None:
    await callback_query.message.delete()
    await callback_query.answer()

    data = await state.get_data()
    announcement_id = data.get('id')
    try:
        stats = await AdminPanelService.broadcast_announcement(
            session=session,
            bot=bot,
            announcement_id=announcement_id
        )
        await callback_query.message.answer(
            text=_(
                '📤 Broadcast completed:\n\n'
                '✅ Delivered: <b>{success}</b>\n'
                '❌ Failed: <b>{failed}</b>'
            ).format(success=stats['success'], failed=stats['failed']),
            reply_markup=get_back_to_announcement_details_kb()
        )
    except ValueError as e:
        await callback_query.message.answer(f'❌ Error: {str(e)}')
    except Exception as e:
        logging.error(f'Unexpected error in broadcast_announcement_handler: {e}')
        await callback_query.message.answer('❌ An unexpected error occurred.')


@announcements_router.callback_query(F.data == 'back_to_announcements')
async def back_to_announcements_handler(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    text = await show_announcements_text(session)
    await state.clear()
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_announcements_kb()
    )


@announcements_router.callback_query(F.data == 'back_to_announcement_details')
async def back_to_announcement_details_handler(
        callback_query: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
) -> None:
    try:
        data = await state.get_data()
        announcement_id = data.get('id')
        if not announcement_id:
            await callback_query.message.answer(
                text=_('⚠️ Announcement ID not found. Please select it again.'),
                reply_markup=get_back_to_announcements_kb()
            )
            return
        await callback_query.message.delete()
        await show_announcement_details(
            target=callback_query.message,
            announcement_id=announcement_id,
            session=session,
            state=state
        )
        await callback_query.answer()

    except Exception as e:
        logger.error(f'Error in back_to_announcement_details_handler: {e}')
        await callback_query.message.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_back_to_announcements_kb()
        )


async def show_announcement_details(target, announcement_id: int, session: AsyncSession,
                                    state: FSMContext = None, reply_markup=None) -> None:
    try:
        announcement = await AnnouncementRepository.get_announcement_by_id(session, announcement_id)
        english_text = next(
            (translation.text for translation in announcement.languages if translation.language_code == 'en'),
            None
        )
        language_codes = [translation.language_code for translation in announcement.languages]

        if state:
            await state.update_data(
                id=announcement_id,
                languages=language_codes
            )

        text = _(
            '🔅 <b>ID: {announcement_id}</b>\n'
            '🔖 <b>Title:</b> {title}\n\n'
            '🌏 <b>Languages:</b> {languages}\n\n'
            '📙 <b>Text:</b> {text}'
        ).format(
            announcement_id=announcement.id,
            title=announcement.title,
            languages=', '.join(language_codes),
            text=english_text or _('No text available.')
        )

        if not announcement.image_url:
            await target.answer(
                text=text,
                reply_markup=reply_markup or get_announcement_menu_kb()
            )
            return

        await target.answer_photo(
            photo=FSInputFile(announcement.image_url),
            caption=text,
            reply_markup=reply_markup or get_announcement_menu_kb()
        )

    except ValueError as e:
        await target.answer(
            text=_('⚠️ {error}').format(error=str(e)),
            reply_markup=get_cancel_announcement_action_kb()
        )
    except Exception as e:
        logger.error(f'Error in show_announcement_details: {e}')
        await target.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_cancel_announcement_action_kb()
        )


async def show_announcements_text(session: AsyncSession) -> str:
    announcements = await AnnouncementRepository.get_all_announcements_with_languages(session)

    if not announcements:
        return _('No announcements yet.')
    posts = []
    for ann in announcements:
        lang_list = (
            ', '.join(lang.language_code for lang in ann.languages
            ) if ann.languages else _('No translations available')
        )
        posts.append(_(
            '🔅 <b>ID:</b> <code>{id}</code>\n'
            '🔖 <b>Title:</b> {title}\n'
            '🌏 <b>Languages:</b> {languages}'
        ).format(id=ann.id, title=ann.title, languages=lang_list))

    return _('📌 <b><i>All announcements:</i></b>\n\n') + '\n\n'.join(posts)
