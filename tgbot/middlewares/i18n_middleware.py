from aiogram.utils.i18n import I18nMiddleware
from typing import Any
from tgbot.database import Database
from aiogram.types import TelegramObject



class CustomI18nMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: TelegramObject, data: dict[str, Any]) -> str:
        db: Database = data.get("db")
        if db:
            user_id = action.from_user.id
            user_language = await db.get_user_language(user_id)
            if user_language:
                return user_language
        return 'en'
