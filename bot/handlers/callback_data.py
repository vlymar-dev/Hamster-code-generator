from aiogram.filters.callback_data import CallbackData


class PaginationCallbackData(CallbackData, prefix='page'):
    game_name: str
    current_page: int
