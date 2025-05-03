from aiogram.fsm.state import State, StatesGroup


class AdminPanelState(StatesGroup):
    current_user_role = State()
    target_user_id = State()
