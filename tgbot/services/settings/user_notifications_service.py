from aiogram.utils.i18n import gettext as _

from infrastructure.repositories.user_repo import UserRepository


class UserNotificationsService:

    @staticmethod
    async def unsubscribe_user(user_id: int, user_repo: UserRepository) -> str:
        """
        Handles the logic for unsubscribing a user and returns an appropriate message.
        """
        result = await user_repo.unsubscribe_notifications(user_id)

        if result == 'Unsubscribe successful':
            return _('You have successfully unsubscribed from notifications.')
        elif result == 'error':
            return _('An error occurred while trying to unsubscribe. Please try again later.')
        else:
            return _('You do not meet the requirements to unsubscribe from notifications.')

    @staticmethod
    async def subscribe_user(user_id: int, user_repo: UserRepository) -> str:
        """
        Handles the logic for subscribing a user and return message.
        """
        await user_repo.subscribe_notifications(user_id)
        return _('You have successfully Subscribed for notifications.')

    @staticmethod
    async def get_subscription_status(user_id: int, user_repo: UserRepository) -> tuple[str, bool]:
        """
        Returns a message about the subscription status
        """
        is_subscribed = await user_repo.get_subscription_status(user_id)
        if is_subscribed:
            return _('Your subscription status: Subscribed'), is_subscribed
        else:
            return _('Your subscription status: Unsubscribed'), is_subscribed
