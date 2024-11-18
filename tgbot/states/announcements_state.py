from aiogram.fsm.state import State, StatesGroup


class CreateAnnouncementState(StatesGroup):
    announcement_title = State()
    announcement_image = State()



class AnnouncementDetailState(StatesGroup):
    announcement_id = State()
