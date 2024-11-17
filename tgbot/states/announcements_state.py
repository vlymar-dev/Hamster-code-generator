from aiogram.fsm.state import State, StatesGroup


class CreateAnnouncementState(StatesGroup):
    announcement_title = State()
    announcement_text = State()
    announcement_image = State()
