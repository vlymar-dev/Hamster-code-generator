import logging
from datetime import datetime
from typing import Optional, Tuple

from aiogram.utils.i18n import gettext as _
from sqlalchemy.exc import DatabaseError

from infrastructure.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

ACHIEVEMENTS = {
    'newcomer': {'keys': 200, 'referrals': 1, 'days': 10},
    'adventurer': {'keys': 201, 'referrals': 0, 'days': 20},
    'bonus_hunter': {'keys': 450, 'referrals': 5, 'days': 30},
    'code_expert': {'keys': 500, 'referrals': 10, 'days': 60},
    'game_legend': {'keys': 700, 'referrals': 20, 'days': 90},
    'absolute_leader': {'keys': 1200, 'referrals': 50, 'days': 120},
}

class UserProgressService:

    @staticmethod
    def calculate_days_in_bot(registration_date: datetime) -> int:
        """
    Calculate the number of days the user has been in the bot.

    Args:
        registration_date: The date when the user registered.

    Returns:
        Number of days since registration.
    """
        try:
            return (datetime.now().date() - registration_date.date()).days
        except AttributeError as e:
            logger.error(f"Invalid registration date provided: {e}")
            return 0

    @staticmethod
    def generate_progress_bar(current: int, total: int, length: int = 10) -> str:
        """
        Generate a visual progress bar for the user's achievements.

        Returns:
            A string representing the progress bar with completion status.
        """
        if total <= 0:
            return '▱' * length + f' (0/{total}) ❌'
        progress = min(int((current / total) * length), length)
        bar = '▰' * progress + '▱' * (length - progress)
        status = '✔️' if current >= total else '❌'
        return f'{bar} ({current}/{total}) {status}'

    @staticmethod
    def calculate_achievement(total_keys: int, referrals: int, days_in_bot: int) -> tuple[str, Optional[str]]:
        """
        Determine the user's current level and the next level based on progress.

        Returns:
            A tuple with the current level and the next level, if any.
        """
        levels = list(ACHIEVEMENTS.keys())
        current_level = 'newcomer'
        next_level = None

        for idx, level in enumerate(levels):
            thresholds = ACHIEVEMENTS[level]
            if (
                total_keys >= thresholds['keys'] and
                referrals >= thresholds['referrals'] and
                days_in_bot >= thresholds['days']
            ):
                current_level = level
                if idx + 1 < len(levels):
                    next_level = levels[idx + 1]
                else:
                    next_level = None  # Max level reached
            else:
                next_level = level
                break

        return current_level, next_level

    @staticmethod
    def get_achievement_text(key: str) -> str:
        """Returns the translated text of the achievement key."""
        achievements = {
            'newcomer': _(
                '🌱 <b>Level:</b>\n<i>Newcomer</i> — <i>You\'ve just begun your journey! '
                'Keep going, there are many opportunities ahead!</i> 🚀'),
            'adventurer': _(
                '🎩 <b>Level:</b>\n<i>Adventurer</i> — <i>You\'ve unlocked a few doors, but more valuable keys await you.</i> 💎'),
            'bonus_hunter': _(
                '🎯 <b>Level:</b>\n<i>Bonus Hunter</i> — <i>With each new key, you grow stronger. Unlock bonuses!</i> 🎁'),
            'code_expert': _(
                '🧠 <b>Level:</b>\n<i>Code Expert</i> — <i>You already know how the system works. Keep improving!</i> 📈'),
            'game_legend': _(
                '🌟 <b>Level:</b>\n<i>Game Legend</i> — <i>You\'ve achieved almost everything! Stay at the top and collect all the keys!</i> 🏅'),
            'absolute_leader': _(
                '👑 <b>Level:</b>\n<i>Absolute Leader</i> — <i>You\'re at the top! All the keys are at your disposal, and you\'re a role model for everyone!</i> 🌍')
        }
        return achievements.get(key, achievements['newcomer'])

    @staticmethod
    def get_status_text(key: str) -> str:
        """Returns the translated status text by key."""
        statuses = {
            'free': _('🎮 <b>Regular Player</b> — Get keys and open doors to become stronger. 🚀'),
            'friend': _(
                '🤝 <b>Friend of the Project</b> — You have access to exclusive features, but there\'s more ahead! 🔥'),
            'premium': _('👑 <b>Elite Player!</b> Use all your privileges and enjoy exclusive content. ✨')
        }
        return statuses.get(key, statuses['free'])

    @staticmethod
    async def generate_user_progress(user_id: int, user_repo: UserRepository) -> Optional[str]:
        """
        Create a detailed progress report for the user.

        Retrieves user data, calculates the current and next achievement levels,
        and formats progress bars for keys, referrals, and days in the bot.

        Returns:
            Optional[dict]: A dictionary containing progress details or None if the user data is unavailable.
        """
        try:
            user_data = await user_repo.get_user_progress(user_id)
            if not user_data:
                return None

            days_in_bot = UserProgressService.calculate_days_in_bot(user_data['registration_date'])
            total_keys_generated = user_data['total_keys_generated']
            referrals = user_data['referrals']
            user_status = user_data['user_status']

            current_level, next_level = UserProgressService.calculate_achievement(
                total_keys=total_keys_generated,
                referrals=referrals,
                days_in_bot=days_in_bot
            )

            achievement = UserProgressService.get_achievement_text(current_level)
            user_status_text = UserProgressService.get_status_text(user_status)

            if next_level:
                next_thresholds = ACHIEVEMENTS[next_level]
                keys_progress = UserProgressService.generate_progress_bar(
                    total_keys_generated, next_thresholds['keys'])
                referrals_progress = UserProgressService.generate_progress_bar(
                    referrals, next_thresholds['referrals'])
                days_progress = UserProgressService.generate_progress_bar(
                    days_in_bot, next_thresholds['days'])
            else:
                keys_progress = _('Max level achieved ✔️')
                referrals_progress = _('Max level achieved ✔️')
                days_progress = _('Max level achieved ✔️')

            progress_text = _(
                '🏆 <b>Progress:</b>\n\n'
                '{achievement_name}\n\n'
                '🔝 <b>To the next level:</b>\n'
                '🔑 <i>Keys:</i> {keys_progress}\n'
                '📨 <i>Referrals:</i> {referrals_progress}\n'
                '⏳ <i>Days in Bot:</i> {days_progress}\n\n'
                '🥇 <b>Your status:</b>\n'
                '{user_status}\n\n'
                '🎳 Invite friends, earn keys, and reach new heights with us! 🌍'
            ).format(
                achievement_name=achievement,
                keys_progress=keys_progress,
                referrals_progress=referrals_progress,
                days_progress=days_progress,
                user_status=user_status_text
            )
            return progress_text
        except DatabaseError as e:
            logger.error(f"Database error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in generate_user_progress: {e}")
            return None
