from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import PromoCodeReceiveSchema
from db.repositories import PromoCodeRepository


class PromoCodeService:

    @staticmethod
    async def consume_promo_codes(session: AsyncSession, game_names: list[str]) -> dict[str, str | None]:
        promo_codes: list[PromoCodeReceiveSchema] = await PromoCodeRepository.get_promo_codes(session, game_names)
        result = {game_name: None for game_name in game_names}
        ids_to_delete = []

        for game_code in promo_codes:
            if game_code.game_name in result:
                result[game_code.game_name] = game_code.promo_code
                ids_to_delete.append(game_code.id)

        if ids_to_delete:
            await PromoCodeRepository.delete_promo_codes(session, ids_to_delete)

        return result
