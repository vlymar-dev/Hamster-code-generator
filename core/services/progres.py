import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.shemas import UserProgresSchema, UserProgressData
from db.repositories import ReferralsRepository, UserRepository

logger = logging.getLogger(__name__)

ACHIEVEMENTS: dict[str, dict[str, int]] = {
    'newcomer': {'keys': 200, 'referrals': 1, 'days': 10},
    'adventurer': {'keys': 201, 'referrals': 0, 'days': 20},
    'bonus_hunter': {'keys': 450, 'referrals': 5, 'days': 30},
    'code_expert': {'keys': 500, 'referrals': 10, 'days': 60},
    'game_legend': {'keys': 700, 'referrals': 20, 'days': 90},
    'absolute_leader': {'keys': 1200, 'referrals': 50, 'days': 120},
}


class ProgressService:

    async def get_user_progres(self, session: AsyncSession, user_id: int):
        user_data: UserProgresSchema = await UserRepository.get_user_progress(session, user_id)

        referrals = await ReferralsRepository.get_count_user_referrals_by_user_id(session, user_id)

        days_in_bot = (datetime.now().date() - user_data.registration_date.date()).days

        current_level, next_level = self.calculate_achievement(user_data.total_keys_generated, referrals, days_in_bot)

        next_thresholds = ACHIEVEMENTS.get(next_level, {})
        keys_progress = self.generate_progress_bar(user_data.total_keys_generated, next_thresholds.get('keys', 0))
        referrals_progress = self.generate_progress_bar(referrals, next_thresholds.get('referrals', 0))
        days_progress = self.generate_progress_bar(days_in_bot, next_thresholds.get('days', 0))

        return UserProgressData(
            total_keys=user_data.total_keys_generated,
            user_status=user_data.user_status,
            days_in_bot=days_in_bot,
            referrals=referrals,
            current_level=current_level,
            next_level=next_level,
            keys_progress=keys_progress,
            referrals_progress=referrals_progress,
            days_progress=days_progress,
        )

    @staticmethod
    def calculate_achievement(total_keys: int, referrals: int, days_in_bot: int) -> tuple[str, Optional[str]]:
        """Determine the user's current level and the next level based on progress."""
        levels = list(ACHIEVEMENTS.keys())

        for i, level in enumerate(levels):
            thresholds = ACHIEVEMENTS[level]
            if total_keys < thresholds['keys'] or referrals < thresholds['referrals'] or days_in_bot < thresholds[
                'days']:
                return levels[max(i - 1, 0)], level

        return levels[-1], None

    @staticmethod
    def generate_progress_bar(current: int, total: int, length: int = 10) -> str:
        """Generate a visual progress bar for the user's achievements."""
        if total <= 0:
            return '▱' * length + f' (0/{total}) ❌'

        progress = min(int((current / total) * length), length)

        return f"{'▰' * progress}{'▱' * (length - progress)} ({current}/{total}) {'✔️' if current >= total else '❌'}"
