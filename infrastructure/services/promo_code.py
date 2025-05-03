import logging

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.dao import PromoCodeDAO
from infrastructure.schemas import PromoCodeReceiveSchema

logger = logging.getLogger(__name__)


class PromoCodeService:
    """Service for managing promo code consumption operations"""

    @staticmethod
    async def consume_promo_codes(session: AsyncSession, game_names: list[str]) -> dict[str, str | None]:
        """Retrieve and consume promo codes for specified games"""
        try:
            logger.debug(f'Consuming promo codes for games: {game_names}')
            promo_codes: list[PromoCodeReceiveSchema] = await PromoCodeDAO.find_by_game_names(session, game_names)
            logger.debug(f'Found {len(promo_codes)} promo codes to process')

            result = {game_name: None for game_name in game_names}
            ids_to_delete = []

            for game_code in promo_codes:
                if game_code.game_name in result:
                    result[game_code.game_name] = game_code.promo_code
                    ids_to_delete.append(game_code.id)

            if ids_to_delete:
                logger.debug(f'Deleting {len(ids_to_delete)} used promo codes')
                await PromoCodeDAO.delete_by_ids(session, ids_to_delete)

            return result
        except Exception as e:
            logger.error(f'Error consuming promo codes: {e}', exc_info=True)
            raise
