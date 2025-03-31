from aiogram.fsm.state import State, StatesGroup


class AdminPanelState(StatesGroup):
    change_role_user_id = State()