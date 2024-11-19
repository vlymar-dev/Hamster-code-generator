from aiogram.fsm.state import State, StatesGroup


class CreateAnnouncementState(StatesGroup):
    announcement_title = State()
    announcement_image = State()



class AnnouncementDetailState(StatesGroup):
    announcement_id = State()
    text_languages = State()
    language_code = State()
    translation_text = State()


class AnnouncementDeleteState(StatesGroup):
    announcement_id = State()
