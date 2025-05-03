from aiogram.fsm.state import State, StatesGroup


class CreateAnnouncement(StatesGroup):
    title = State()
    image = State()


class AnnouncementDetails(StatesGroup):
    id = State()
    languages = State()
    language_code = State()
    translation_text = State()
    edit_translation_text = State()


class DeleteAnnouncement(StatesGroup):
    id = State()
