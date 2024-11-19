from aiogram.fsm.state import State, StatesGroup


class CreateAnnouncement(StatesGroup):
    Title = State()
    Image = State()



class AnnouncementDetails(StatesGroup):
    ID = State()
    Languages = State()
    LanguageCode = State()
    TranslationText = State()


class DeleteAnnouncement(StatesGroup):
    ID = State()
