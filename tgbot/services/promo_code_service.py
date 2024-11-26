import logging
from typing import Optional

from infrastructure.repositories.promo_code_repo import PromoCodeRepository

logger = logging.getLogger(__name__)


class PromoCodeService:

    @staticmethod
    async def get_code_count_for_game(game_name: str, promo_code_repo: PromoCodeRepository) -> int:
        try:
            return await promo_code_repo.get_code_count_for_game(game_name)
        except Exception as e:
            logger.error(f'Error retrieving promo code counts: {e}')
            raise

    @staticmethod
    async def pop_one_code_per_game(game_name: str, promo_code_repo: PromoCodeRepository) -> Optional[str]:
        """
        Get and remove one promo code for the specified game.
        """
        try:
            promo_code = await promo_code_repo.pop_code_by_game(game_name)
            if not promo_code:
                logger.info(f'There are no promo codes available for the game: {game_name}')
                return None
            logger.info(f'Promo code for the game has been issued {game_name}: {promo_code}')
            return promo_code
        except Exception as e:
            logger.error(f'Error when receiving and deleting a promo code for the game {game_name}: {e}')
            raise
