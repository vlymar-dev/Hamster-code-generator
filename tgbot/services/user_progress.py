import logging
from typing import Optional

from sqlalchemy.exc import DatabaseError

from tgbot.database import Database
from tgbot.services.progress_calculator import calculate_achievement, calculate_days_in_bot
from tgbot.services.text_provider import get_achievement_text, get_status_text

logger = logging.getLogger(__name__)


async def generate_user_progress(user_id: int, db: Database) -> Optional[dict]:
    """
    Generates user progress based on data from the database.

    :param user_id: User ID.
    :param db: Database instance.
    :return: Dictionary with user statistics or None if no user is found.
    """
    try:
        user_data = await db.get_user_progress(user_id)
        if not user_data:
            return None

        days_in_bot = calculate_days_in_bot(user_data['registration_date'])
        total_keys_generated = user_data['total_keys_generated']
        referrals = user_data['referrals']
        user_status = user_data['user_status']

        achievement_key = calculate_achievement(
            total_keys=total_keys_generated,
            referrals=referrals,
            days_in_bot=days_in_bot
        )
        achievement = get_achievement_text(achievement_key)
        user_status = get_status_text(user_status)
        return {
            'achievement_name': achievement,
            'keys_total': total_keys_generated,
            'referrals': referrals,
            'user_status': user_status,
        }
    except DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in generate_user_stats: {e}")
        return None

