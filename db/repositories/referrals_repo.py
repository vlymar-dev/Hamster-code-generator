from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Referral


class ReferralsRepository:

    @staticmethod
    async def get_count_user_referrals_by_user_id(session: AsyncSession, user_id: int) -> int | None:
        result = await session.execute(
            select(func.count(Referral.id)).where(Referral.referrer_id == user_id)
        )
        total_refs = result.scalar_one_or_none()
        return total_refs if total_refs else 0
