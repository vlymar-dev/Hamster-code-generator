from aiogram.fsm.state import State, StatesGroup


class UserLeaveFeedback(StatesGroup):
    writing_feedback = State()


class AdminReplyToFeedback(StatesGroup):
    waiting_for_reply = State()
