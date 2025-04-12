import logging

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import ReferralAddingSchema
from db.models import Referral

logger = logging.getLogger(__name__)

class ReferralsRepository:

    @staticmethod
    async def add_referral(session: AsyncSession, referrals_data: ReferralAddingSchema):
        try:
            new_instance = Referral(**referrals_data.model_dump())
            session.add(new_instance)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding referral: {e}')
            raise

    @staticmethod
    async def get_count_user_referrals_by_user_id(session: AsyncSession, user_id: int) -> int | None:
        try:
            result = await session.execute(
                select(func.count(Referral.id)).where(Referral.referrer_id == user_id)
            )
            total_refs = result.scalar_one_or_none()
            return total_refs if total_refs else 0
        except SQLAlchemyError as e:
            logger.error(f'Database error occurred while getting count referrals by user_id= {user_id}: {e}')
            raise
