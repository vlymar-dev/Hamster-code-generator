from aiogram.utils.i18n import gettext as _

from tgbot.database import Database
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware


class LanguageService:

    @staticmethod
    async def update_language(user_id: int, language_code: str, i18n: CustomI18nMiddleware, db: Database) -> str:
        await db.update_user_language(user_id, language_code)
        i18n.ctx_locale.set(language_code)
        return _("Language updated!")