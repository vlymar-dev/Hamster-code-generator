from aiogram.fsm.state import State, StatesGroup


class AddGameCode(StatesGroup):
    GameName = State()
    Question = State()
    Answer = State()


class DeleteGameCode(StatesGroup):
    ID = State()
