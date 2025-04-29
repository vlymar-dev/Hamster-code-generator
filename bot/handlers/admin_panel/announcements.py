import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.admin_panel.announcements_kb import (
    get_announcement_menu_kb,
    get_announcements_kb,
    get_back_to_announcement_details_kb,
    get_back_to_announcements_kb,
    get_cancel_announcement_action_kb,
    get_confirmation_broadcast_kb,
    get_confirmation_translate_deletion,
    get_languages_kb,
)
from bot.states import AnnouncementDetails, CreateAnnouncement, DeleteAnnouncement
from bot.utils import static_data
from infrastructure.db.dao import AnnouncementDAO, AnnouncementTranslationDAO
from infrastructure.schemas import (
    AnnouncementCreateSchema,
    AnnouncementTranslationCreateSchema,
    AnnouncementTranslationTextSchema,
)
from infrastructure.services import AdminPanelService

logger = logging.getLogger(__name__)
announcements_router = Router()


@announcements_router.callback_query(F.data == 'manage_announcements')
async def manage_announcements_handler(callback_query: CallbackQuery, session_without_commit: AsyncSession) -> None:
    """Handle request to manage announcements."""
    admin_id = callback_query.message.message_id
    logger.debug(f'Admin {admin_id} entered announcements management')

    try:
        text = await show_announcements_text(session_without_commit)
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(text=text, reply_markup=get_announcements_kb())
        logger.info(f'Admin {admin_id} opened announcements list')
    except Exception as e:
        logger.error(f'Announcements error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'create_announcement')
async def create_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Initiate announcement creation process."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} started creating announcement')

    try:
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('📝 Enter the announcement title:'), reply_markup=get_cancel_announcement_action_kb()
        )
        await state.set_state(CreateAnnouncement.title)
        logger.info(f'Admin {admin_id} entered announcement creation flow')
    except Exception as e:
        logger.error(f'Creating announcement error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.message(CreateAnnouncement.title)
async def process_announcement_title_handler(message: Message, state: FSMContext) -> None:
    """Process announcement title input."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} processing title input')

    try:
        await state.update_data(title=message.html_text)
        await state.set_state(CreateAnnouncement.image)
        await message.answer(
            text=_('📝 <b>Title:</b>\n{title}\n\nSend an image or type <code>no_image</code> to skip.').format(
                title=message.html_text
            ),
            reply_markup=get_cancel_announcement_action_kb(),
        )
        logger.info(f'Admin {message.from_user.id} entered title: {message.text[:50]}...')
    except Exception as e:
        logger.error(f'Process title announcement error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.message(CreateAnnouncement.image)
async def process_announcement_image_handler(
    message: Message, state: FSMContext, session_with_commit: AsyncSession, bot: Bot
) -> None:
    """Process image input for announcement creation."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} processing image input')

    try:
        data = await state.get_data()
        if message.photo:
            try:
                photo = message.photo[-1]
                logger.info(f'Admin {admin_id} sent photo for announcement')
                image_url = await AdminPanelService.process_and_save_image(photo, bot)
                data = AnnouncementCreateSchema(
                    title=data['title'], created_by=message.from_user.id, image_url=image_url
                )
                await AnnouncementDAO.add(session_with_commit, data)
                await message.answer(
                    text=_('✅ Announcement "{title}" with image created.').format(title=data.title),
                    reply_markup=get_back_to_announcements_kb(),
                )
                logger.info(f'Admin {admin_id} created announcement with image')
            except ValueError as ve:
                logger.warning(f'Admin {admin_id} sent invalid image: {ve}')
                await message.answer(
                    text=_('🚫 Unsupported image format. Please send a correct image.'),
                    reply_markup=get_cancel_announcement_action_kb(),
                )
            except Exception as e:
                logger.error(f'Image processing error: {e}', exc_info=True)
                await message.answer(
                    text=_('⚠️ Error processing image. Please try again.'),
                    reply_markup=get_cancel_announcement_action_kb(),
                )

        elif message.text.lower().strip() in ['no_image']:
            data = AnnouncementCreateSchema(title=data['title'], created_by=message.from_user.id)
            await AnnouncementDAO.add(session_with_commit, data)

            await message.answer(
                text=_('✅ Announcement "{title}" without image created.').format(title=data.title),
                reply_markup=get_back_to_announcements_kb(),
            )
            logger.info(f'Admin {admin_id} created announcement without image')
        else:
            await message.answer(
                text=_('Please submit an image or enter <code>no_image</code> to skip.'),
                reply_markup=get_cancel_announcement_action_kb(),
            )
        await state.clear()
    except Exception as e:
        logger.error(f'Process adding image announcement error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'view_announcement_detail')
async def view_announcement_detail_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle request to view announcement details by ID."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} requested announcement details')

    try:
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('📝 Enter the announcement id:'), reply_markup=get_cancel_announcement_action_kb()
        )
        await state.set_state(AnnouncementDetails.id)
        logger.info(f'Admin {admin_id} entering announcement ID input')
    except Exception as e:
        logger.error(f'View announcement by ID error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.message(AnnouncementDetails.id)
async def process_announcement_id_input(
    message: Message, state: FSMContext, session_without_commit: AsyncSession
) -> None:
    """Process announcement ID input for details viewing."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} processing announcement ID input')

    try:
        announcement_id = int(message.text)
        logger.info(f'Admin {admin_id} requested details for announcement {announcement_id}')
        await show_announcement_details(
            target=message, announcement_id=announcement_id, session=session_without_commit, state=state
        )
    except ValueError as ve:
        logger.warning(f'Invalid ID input from admin {admin_id}: {message.text}')
        await message.answer(
            text=_('⚠️ {error}').format(error=str(ve)), reply_markup=get_cancel_announcement_action_kb()
        )
    except Exception as e:
        logger.error(f'Process announcement ID error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'create_announcement_translation')
async def create_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle request to create new translation for announcement."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} creating translation')

    try:
        data = await state.get_data()
        if 'languages' not in data:
            logger.warning(f'Admin {admin_id} tried creating translation without context')
            await callback_query.answer(_('⚠️ First select an announcement!'), show_alert=True)
            return

        available_languages = {
            key: value for key, value in static_data.LANGUAGES_DICT.items() if key not in data['languages']
        }
        await callback_query.message.delete()
        await callback_query.answer()
        if available_languages:
            logger.info(f'Admin {admin_id} selecting from {len(available_languages)} languages')
            await callback_query.message.answer(
                text=_('🌏 Select a language from the available languages:'),
                reply_markup=get_languages_kb(available_languages, 'add_translation_text_'),
            )
            return
        logger.debug(f'No available languages for admin {admin_id}')
        await callback_query.message.answer(
            text=_('⚠️ No available languages.'), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'Create announcement translation error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data.startswith('add_translation_text_'))
async def get_add_translation_text_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection for new translation."""
    admin_id = callback_query.from_user.id
    language_code: str = callback_query.data.split('_')[-1]
    logger.info(f'Admin {admin_id} selected language: {language_code}')

    try:
        await state.update_data(language_code=language_code)
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('📝 Enter the announcement text for "{language_code}":').format(
                language_code=static_data.LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb(),
        )
        await state.set_state(AnnouncementDetails.translation_text)
    except Exception as e:
        logger.error(f'Get announcement translation error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.message(AnnouncementDetails.translation_text)
async def process_translation_text_input(
    message: Message, state: FSMContext, session_with_commit: AsyncSession
) -> None:
    """Process translation text input and save to database."""
    admin_id = message.from_user.id
    data = await state.get_data()
    language_code = data['language_code']
    logger.debug(f'Admin {admin_id} adding translation for {language_code}')

    try:
        await AnnouncementTranslationDAO.add(
            session=session_with_commit,
            values=AnnouncementTranslationCreateSchema(
                announcement_id=int(data['id']), text=message.html_text, language_code=language_code
            ),
        )
        logger.info(f'Admin {admin_id} added {language_code} translation')
        await message.answer(
            text=_("✅ Translation for: '{language}' created").format(
                language=static_data.LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb(),
        )
        data.pop('language_code', None)
        await state.update_data(**data)
    except ValueError as ve:
        await message.answer(
            text=_('❌ {error}').format(error=str(ve)), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'Translation text input error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'edit_announcement_translation')
async def edit_announcement_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle request to edit existing translation."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} initiated translation edit')

    try:
        data = await state.get_data()
        available_languages = {
            key: value for key, value in static_data.LANGUAGES_DICT.items() if key in data['languages']
        }

        await callback_query.message.delete()
        await callback_query.answer()
        if available_languages:
            await callback_query.message.answer(
                text=_('🌏 Select the language available for editing:'),
                reply_markup=get_languages_kb(available_languages, 'edit_translation_text_'),
            )
            return
        logger.info(f'No editable translations for admin {admin_id}')
        await callback_query.message.answer(
            text=_('⚠️ No available translations for editing.'), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'Translation edit error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data.startswith('edit_translation_text_'))
async def get_edit_translation_text_handler(
    callback_query: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
) -> None:
    """Handle language selection for translation editing."""
    admin_id = callback_query.from_user.id
    language_code: str = callback_query.data.split('_')[-1]
    logger.debug(f'Admin {admin_id} editing {language_code} translation')

    try:
        data = await state.get_data()
        if 'id' not in data:
            logger.error('Missing announcement ID in state')
            await callback_query.answer(_('⚠️ Announcement context lost!'), show_alert=True)
            return

        ann_tr = await AnnouncementTranslationDAO.find_by_announcement_and_language(
            session=session_without_commit, announcement_id=int(data['id']), language_code=language_code
        )
        await state.update_data(language_code=language_code, translation_id=ann_tr.id)
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=(
                _('📙 <b>Text: </b>\n')
                + f'{ann_tr.text}\n\n'
                + _('📝 Enter new announcement text for "{language_code}":').format(
                    language_code=static_data.LANGUAGES_DICT.get(language_code)
                )
            ),
            reply_markup=get_back_to_announcement_details_kb(),
        )
        await state.set_state(AnnouncementDetails.edit_translation_text)
    except Exception as e:
        logger.error(f'Language selection for editing text error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.message(AnnouncementDetails.edit_translation_text)
async def process_edit_translation_text_input(
    message: Message, state: FSMContext, session_with_commit: AsyncSession
) -> None:
    """Process updated translation text input."""
    admin_id = message.from_user.id
    data = await state.get_data()
    language_code = data['language_code']
    translation_id = data['translation_id']
    logger.debug(f'Admin {admin_id} updating {language_code} translation')

    try:
        await AnnouncementTranslationDAO.update(
            session=session_with_commit,
            data_id=translation_id,
            values=AnnouncementTranslationTextSchema(text=message.html_text),
        )

        await message.answer(
            text=_("✅ Translation updated <b>successfully</b> for: '{language}'.").format(
                language=static_data.LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb(),
        )
        logger.info(f'Translation {language_code} updated successfully')
        data.pop('language_code', None)
        data.pop('translation_id', None)
        await state.update_data(**data)
    except ValueError as ve:
        logger.warning(f'Validation error updating translation: {ve}')
        await message.answer(
            text=_('❌ {error}').format(error=str(ve)), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'Update translation error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'delete_announcement')
async def delete_announcement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Initiate announcement deletion process."""
    admin_id = callback_query.from_user.id
    logger.info(f'Admin {admin_id} starting deletion process')

    try:
        await state.clear()
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('📝 Enter the announcement id to delete:'), reply_markup=get_cancel_announcement_action_kb()
        )
        await state.set_state(DeleteAnnouncement.id)
        logger.debug('Deletion state initialized')
    except Exception as e:
        logger.error(f'Deletion initiation error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.message(DeleteAnnouncement.id)
async def process_delete_announcement_handler(
    message: Message, session_with_commit: AsyncSession, state: FSMContext
) -> None:
    """Process announcement deletion by ID."""
    admin_id = message.from_user.id
    logger.debug(f'Admin {admin_id} deleting announcement')

    try:
        announcement_id = int(message.text)
        logger.info(f'Deleting announcement {announcement_id} by admin {admin_id}')
        await AnnouncementDAO.delete(session_with_commit, announcement_id)
        await state.clear()
        await message.answer(
            text=_('✅ Announcement with ID: <b>{id}</b> has been deleted.').format(id=announcement_id),
            reply_markup=get_back_to_announcements_kb(),
        )
        logger.info(f'Announcement {announcement_id} deleted successfully')
    except ValueError as ve:
        await message.answer(text=_('❌ {error}').format(error=str(ve)), reply_markup=get_back_to_announcements_kb())
        logger.error(f'Deletion announcement error for admin {admin_id}: {ve}', exc_info=True)
    except IntegrityError as ie:
        await message.answer(
            text=_("⚠️ You can't delete an ad if there are translations for it."),
            reply_markup=get_back_to_announcements_kb(),
        )
        logger.error(f'Deletion announcement error for admin {admin_id}: {ie}', exc_info=True)
    except Exception as e:
        await state.clear()
        await message.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_back_to_announcements_kb(),
        )
        logger.error(f'Deletion announcement error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data == 'view_announcement_translation')
async def view_announcement_translation_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle request to view existing translations."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} viewing translations')

    try:
        data = await state.get_data()

        if 'languages' not in data:
            logger.warning('Missing languages data in state')
            await callback_query.answer(_('⚠️ Announcement context lost!'), show_alert=True)
            return

        languages_dict = {key: value for key, value in static_data.LANGUAGES_DICT.items() if key in data['languages']}
        await callback_query.message.delete()
        await callback_query.answer()
        if languages_dict:
            logger.info(f'Showing {len(languages_dict)} translations')
            await callback_query.message.answer(
                text=_('🌏 Select a language from the list of available languages:'),
                reply_markup=get_languages_kb(languages_dict, 'view_translation_text_'),
            )
            return
        await callback_query.message.answer(
            text=_('⚠️ No available translations to view.'), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'View announcements error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data.startswith('view_translation_text_'))
async def get_view_translation_text_handler(
    callback_query: CallbackQuery, session_without_commit: AsyncSession, state: FSMContext
) -> None:
    """Display selected translation text."""
    admin_id = callback_query.from_user.id
    language_code = callback_query.data.split('_')[-1]
    logger.debug(f'Admin {admin_id} viewing {language_code} translation')

    try:
        data = await state.get_data()

        if 'id' not in data:
            logger.error('Missing announcement ID in state')
            await callback_query.answer(_('⚠️ Announcement context lost!'), show_alert=True)
            return

        text = await AnnouncementTranslationDAO.find_by_announcement_and_language(
            session=session_without_commit, announcement_id=int(data['id']), language_code=language_code
        )
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(text=text.text, reply_markup=get_back_to_announcement_details_kb())
    except Exception as e:
        logger.error(f'Display translation error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data == 'delete_announcement_translation')
async def delete_translation_text_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle request to delete existing translation."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} initiated translation deleting')

    try:
        data = await state.get_data()
        available_languages = {
            key: value for key, value in static_data.LANGUAGES_DICT.items() if key in data['languages']
        }

        await callback_query.message.delete()
        await callback_query.answer()
        if available_languages:
            await callback_query.message.answer(
                text=_('🌏 Select the language available for deleting:'),
                reply_markup=get_languages_kb(available_languages, 'delete_translation_text_'),
            )
            return
        logger.info(f'No editable translations for admin {admin_id}')
        await callback_query.message.answer(
            text=_('⚠️ No available translations for deleting.'), reply_markup=get_back_to_announcement_details_kb()
        )
    except Exception as e:
        logger.error(f'Translation deleting error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data.startswith('delete_translation_text_'))
async def get_delete_translation_text_handler(
    callback_query: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
) -> None:
    """Handle language selection for translation deleting."""
    admin_id = callback_query.from_user.id
    language_code: str = callback_query.data.split('_')[-1]
    logger.debug(f'Admin {admin_id} deleting {language_code} translation')

    try:
        data = await state.get_data()
        if 'id' not in data:
            logger.error('Missing announcement ID in state')
            await callback_query.answer(_('⚠️ Announcement context lost!'), show_alert=True)
            return

        ann_tr = await AnnouncementTranslationDAO.find_by_announcement_and_language(
            session=session_without_commit, announcement_id=int(data['id']), language_code=language_code
        )
        await state.update_data(language_code=language_code, translation_id=ann_tr.id)
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=(
                _('📙 <b>Text: </b>\n')
                + f'{ann_tr.text}\n\n'
                + _('❌ Do you want to delete this translation for "{language_code}"?').format(
                    language_code=static_data.LANGUAGES_DICT.get(language_code)
                )
            ),
            reply_markup=get_confirmation_translate_deletion(),
        )
    except Exception as e:
        logger.error(f'Language selection for deleting error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'confirm_translation_deletion')
async def confirm_translation_deletion_handler(
    callback_query: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession
) -> None:
    """Process deletion translation text input."""
    admin_id = callback_query.from_user.id
    data = await state.get_data()
    language_code = data['language_code']
    translation_id = data['translation_id']
    logger.debug(f'Admin {admin_id} remove {language_code} translation')

    try:
        await AnnouncementTranslationDAO.delete(session_with_commit, translation_id)
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=_('✅ Announcement translation with language: <b>{language}</b> has been deleted.').format(
                language=static_data.LANGUAGES_DICT.get(language_code)
            ),
            reply_markup=get_back_to_announcement_details_kb(),
        )
        logger.info(f'Translation {language_code} removed successfully')
        data.pop('language_code', None)
        data.pop('translation_id', None)
        await state.update_data(**data)
    except Exception as e:
        logger.error(f'Deletion translation error for admin {admin_id}: {e}', exc_info=True)
        raise


@announcements_router.callback_query(F.data == 'broadcast_announcement')
async def broadcast_announcement_request_handler(callback_query: CallbackQuery) -> None:
    """Handle broadcast confirmation request."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} requesting broadcast')

    try:
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(
            text=_('🫔 Are you sure you want to broadcast this announcement?'),
            reply_markup=get_confirmation_broadcast_kb(),
        )
    except Exception as e:
        logger.error(f'Broadcast confirmation error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data == 'confirm_broadcast')
async def confirm_broadcast_handler(
    callback_query: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession, bot: Bot
) -> None:
    """Handle final confirmation of announcement broadcast."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} confirming broadcast')

    try:
        await callback_query.message.delete()
        await callback_query.answer()

        data = await state.get_data()
        announcement_id = data.get('id')
        if not announcement_id:
            logger.warning('No announcement ID in state during broadcast')
            await callback_query.message.answer(_('⚠️ Announcement not found!'))
            return

        try:
            logger.info(f'Starting broadcast for announcement {announcement_id}')
            stats = await AdminPanelService.broadcast_announcement(
                session=session_without_commit, bot=bot, announcement_id=announcement_id
            )
            logger.info(f'Broadcast stats: {stats}')
            await callback_query.message.answer(
                text=_('📤 Broadcast completed:\n\n✅ Delivered: <b>{success}</b>\n❌ Failed: <b>{failed}</b>').format(
                    success=stats['success'], failed=stats['failed']
                ),
                reply_markup=get_back_to_announcement_details_kb(),
            )
        except ValueError as ve:
            logger.error(f'Broadcast validation error: {ve}')
            await callback_query.message.answer(f'❌ Error: {str(ve)}')
        except Exception as e:
            logger.error(f'Broadcast failed: {e}', exc_info=True)
            logging.error(f'Unexpected error in broadcast_announcement_handler: {e}')
            await callback_query.message.answer('❌ An unexpected error occurred.')
    except Exception as e:
        logger.error(f'Confirm broadcast error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data == 'back_to_announcements')
async def back_to_announcements_handler(
    callback_query: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
) -> None:
    """Handle navigation back to announcements list."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} returning to announcements list')

    try:
        text = await show_announcements_text(session_without_commit)
        await state.clear()
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer(text=text, reply_markup=get_announcements_kb())
        logger.debug('Announcements list displayed')
    except Exception as e:
        logger.error(f'Back to announcements error for admin {admin_id}: {e}', exc_info=True)


@announcements_router.callback_query(F.data == 'back_to_announcement_details')
async def back_to_announcement_details_handler(
    callback_query: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
) -> None:
    """Handle navigation back to announcement details."""
    admin_id = callback_query.from_user.id
    logger.debug(f'Admin {admin_id} returning to details')

    try:
        data = await state.get_data()
        announcement_id = data.get('id')

        if not announcement_id:
            logger.warning('Missing announcement ID in state')
            await callback_query.message.answer(
                text=_('⚠️ Announcement ID not found. Please select it again.'),
                reply_markup=get_back_to_announcements_kb(),
            )
            return
        await callback_query.message.delete()
        await show_announcement_details(
            target=callback_query.message, announcement_id=announcement_id, session=session_without_commit, state=state
        )
        await callback_query.answer()
        logger.debug(f'Re-displayed details for announcement {announcement_id}')
    except Exception as e:
        logger.error(f'Error in back_to_announcement_details_handler: {e}')
        await callback_query.message.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_back_to_announcements_kb(),
        )


async def show_announcement_details(
    target, announcement_id: int, session: AsyncSession, state: FSMContext = None, reply_markup=None
) -> None:
    """Display announcement details with translations."""
    logger.debug(f'Showing details for announcement {announcement_id}')

    try:
        announcement = await AnnouncementDAO.find_by_id_with_languages(session, announcement_id)
        english_text = next(
            (translation.text for translation in announcement.languages if translation.language_code == 'en'), None
        )
        language_codes = [translation.language_code for translation in announcement.languages]

        if state:
            await state.update_data(id=announcement_id, languages=language_codes)

        text = _(
            '🔅 <b>ID: {announcement_id}</b>\n'
            '🔖 <b>Title:</b> {title}\n\n'
            '🌏 <b>Languages:</b> {languages}\n\n'
            '📙 <b>Text:</b> {text}'
        ).format(
            announcement_id=announcement.id,
            title=announcement.title,
            languages=', '.join(language_codes),
            text=english_text or _('No text available.'),
        )

        if not announcement.image_url:
            await target.answer(text=text, reply_markup=reply_markup or get_announcement_menu_kb())
            return

        await target.answer_photo(
            photo=FSInputFile(announcement.image_url),
            caption=text,
            reply_markup=reply_markup or get_announcement_menu_kb(),
        )
        logger.info(f'Displayed details for announcement {announcement_id}')

    except ValueError as ve:
        logger.warning(f'Error showing announcement details: {ve}')
        await target.answer(text=_('⚠️ {error}').format(error=str(ve)), reply_markup=get_cancel_announcement_action_kb())
    except Exception as e:
        logger.error(f'Error in show_announcement_details: {e}', exc_info=True)
        await target.answer(
            text=_('⚠️ An unexpected error occurred. Please try again later.'),
            reply_markup=get_cancel_announcement_action_kb(),
        )


async def show_announcements_text(session: AsyncSession) -> str:
    """Generate formatted text with all announcements."""
    logger.debug('Generating announcements list text')
    try:
        announcements = await AnnouncementDAO.find_all_with_languages(session)

        if not announcements:
            return _('No announcements yet.')
        posts = []
        for ann in announcements:
            lang_list = (
                ', '.join(lang.language_code for lang in ann.languages)
                if ann.languages
                else _('No translations available')
            )
            posts.append(
                _('🔅 <b>ID:</b> <code>{id}</code>\n🔖 <b>Title:</b> {title}\n🌏 <b>Languages:</b> {languages}').format(
                    id=ann.id, title=ann.title, languages=lang_list
                )
            )

        return _('📌 <b><i>All announcements:</i></b>\n\n') + '\n\n'.join(posts)
    except Exception as e:
        logger.error(f'Error in show_announcements_text: {e}', exc_info=True)
        return _('⚠️ Error loading announcements. Please try again later.')
