from aiogram.fsm.state import State, StatesGroup


class PaymentState(StatesGroup):
    amount_entry = State()
