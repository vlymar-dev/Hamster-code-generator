import logging
from typing import Optional

from infrastructure.repositories.promo_code_repo import PromoCodeRepository
from infrastructure.repositories.user_key_repo import UserKeyRepository

logger = logging.getLogger(__name__)


class PromoCodeService:

    @staticmethod
    async def get_key_counts_for_games(game_names: list[str], promo_code_repo: PromoCodeRepository) -> dict[str, int]:
        try:
            return await promo_code_repo.get_code_counts_for_games(game_names)
        except Exception as e:
            logger.error(f'Error while retrieving key counts for games: {e}')
            return {game_name: 0 for game_name in game_names}

    @staticmethod
    async def get_and_delete_promo_codes(game_names: list[str], user_id: int, promo_code_repo: PromoCodeRepository, user_key_repo: UserKeyRepository) -> dict[
        str, Optional[str]]:
        """Get and remove promo codes for a list of games. Updates user key data."""
        try:
            promo_codes = await promo_code_repo.get_promo_codes(game_names)
            if not promo_codes:
                return {game_name: None for game_name in game_names}

            result = {}
            ids_to_delete = []
            for game_name in game_names:
                game_codes = [code for code in promo_codes if code.game_name == game_name]
                if game_codes:
                    result[game_name] = game_codes[0].promo_code
                    ids_to_delete.append(game_codes[0].id)
                else:
                    result[game_name] = None

            await promo_code_repo.delete_promo_codes(ids_to_delete)
            return result
        except Exception as e:
            logger.error(f'Error in get_and_delete_promo_codes: {e}')
            raise
