import logging
from datetime import datetime
from typing import Optional

from aiogram.utils.i18n import gettext as _
from sqlalchemy.exc import DatabaseError

from tgbot.database import Database

logger = logging.getLogger(__name__)

class UserProgressService:

    @staticmethod
    def calculate_days_in_bot(registration_date: datetime) -> int:
        """Calculates the number of days the user has spent in the bot."""
        try:
            return (datetime.now().date() - registration_date.date()).days
        except AttributeError as e:
            logger.error(f"Invalid registration date provided: {e}")
            return 0

    @staticmethod
    def calculate_achievement(total_keys: int, referrals: int, days_in_bot: int) -> str:
        """Determines the user's achievement level based on keys, referrals, and days in the bot."""
        if total_keys > 1200 and referrals > 50 and days_in_bot > 90:
            return 'absolute_leader'
        elif 501 <= total_keys <= 1199 and referrals > 20 and days_in_bot > 60:
            return 'game_legend'
        elif total_keys > 500 and referrals > 10 and days_in_bot > 40:
            return 'code_expert'
        elif total_keys > 450 and (referrals > 5 or days_in_bot > 30):
            return 'bonus_hunter'
        elif total_keys > 201 and days_in_bot > 10:
            return 'adventurer'
        return 'newcomer'

    @staticmethod
    def get_achievement_text(key: str) -> str:
        """Returns the translated text of the achievement key."""
        achievements = {
            'newcomer': _('🌱 <b>Newcomer</b> — <i>You\'ve just begun your journey! Keep going, there are many opportunities ahead!</i> 🚀'),
            'adventurer': _('🔑 <b>Adventurer</b> — <i>You\'ve unlocked a few doors, but more valuable keys await you.</i> 💎'),
            'bonus_hunter': _('🎯 <b>Bonus Hunter</b> — <i>With each new key, you grow stronger. Unlock bonuses!</i> 🎁'),
            'code_expert': _('🧠 <b>Code Expert</b> — <i>You already know how the system works. Keep improving!</i> 📈'),
            'game_legend': _('🌟 <b>Game Legend</b> — <i>You\'ve achieved almost everything! Stay at the top and collect all the keys!</i> 🏅'),
            'absolute_leader': _('👑 <b>Absolute Leader</b> — <i>You\'re at the top! All the keys are at your disposal, and you\'re a role model for everyone!</i> 🌍')
        }
        return achievements.get(key, achievements['newcomer'])

    @staticmethod
    def get_status_text(key: str) -> str:
        """Returns the translated status text by key."""
        statuses = {
            'free': _('🎮 <b>Regular Player</b> — Get keys and open doors to become stronger. 🚀'),
            'friend': _('🤝 <b>Friend of the Project</b> — You have access to exclusive features, but there\'s more ahead! 🔥'),
            'premium': _('👑 <b>Elite Player!</b> Use all your privileges and enjoy exclusive content. ✨')
        }
        return statuses.get(key, statuses['free'])

    @staticmethod
    async def generate_user_progress(user_id: int, db: Database) -> Optional[dict]:
        """
        Generates user progress based on data from the database.

        :param user_id: User ID.
        :param db: Database
        :return: Dictionary with user statistics or None if no user is found.
        """
        try:
            user_data = await db.get_user_progress(user_id)
            if not user_data:
                return None

            days_in_bot = UserProgressService.calculate_days_in_bot(user_data['registration_date'])
            total_keys_generated = user_data['total_keys_generated']
            referrals = user_data['referrals']
            user_status = user_data['user_status']

            achievement_key = UserProgressService.calculate_achievement(
                total_keys=total_keys_generated,
                referrals=referrals,
                days_in_bot=days_in_bot
            )
            achievement = UserProgressService.get_achievement_text(achievement_key)
            user_status_text = UserProgressService.get_status_text(user_status)

            return {
                'achievement_name': achievement,
                'keys_total': total_keys_generated,
                'referrals': referrals,
                'user_status': user_status_text,
            }
        except DatabaseError as e:
            logger.error(f"Database error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in generate_user_progress: {e}")
            return None