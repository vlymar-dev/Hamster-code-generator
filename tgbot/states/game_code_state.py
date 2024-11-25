from aiogram.fsm.state import State, StatesGroup


class GameCodeManagement(StatesGroup):
    WaitingForGameSelection = State()
    WaitingForActionSelection = State()
    WaitingForTask = State()
    WaitingForAnswer = State()
    WaitingForIDToDelete = State()
