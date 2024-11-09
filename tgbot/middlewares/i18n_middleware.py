from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from typing import Any, Optional
from tgbot.database import Database
from aiogram.types import TelegramObject, Update



class CustomI18nMiddleware(SimpleI18nMiddleware):
    def __init__(self, domain: str, path: str):
        self.i18n = I18n(path=path, default_locale="en", domain=domain)
        super().__init__(self.i18n)

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        db: Database = data.get("db")
        user_id: Optional[int] = None

        if isinstance(event, Update):
            if event.message:
                user_id = event.message.from_user.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id

        if db and user_id:
            user_language = await db.get_user_language(user_id)
            if user_language:
                return user_language

        return self.i18n.default_locale
