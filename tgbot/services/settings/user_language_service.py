from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository
from tgbot.middlewares.i18n_middleware import CustomI18nMiddleware


class UserLanguageService:

    @staticmethod
    async def update_language(user_id: int, language_code: str, i18n: CustomI18nMiddleware, user_repo: UserRepository) -> str:
        result = await user_repo.update_user_language(user_id, language_code)
        if result:
            i18n.ctx_locale.set(language_code)
            return _("Language updated!")
        return _("Language update error")