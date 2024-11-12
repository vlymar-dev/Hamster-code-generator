from aiogram.utils.i18n import gettext as _

from tgbot.database import Database


class UserService:

    @staticmethod
    async def unsubscribe_user(user_id: int, db: Database) -> str:
        """
        Handles the logic for unsubscribing a user and returns an appropriate message.
        """
        result = await db.unsubscribe_notifications(user_id)

        if result == 'Unsubscribe successful':
            return _("You have successfully unsubscribed from notifications.")
        elif result == 'error':
            return _("An error occurred while trying to unsubscribe. Please try again later.")
        else:
            return _("You do not meet the requirements to unsubscribe from notifications.")
