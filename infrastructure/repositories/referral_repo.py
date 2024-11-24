import logging

from sqlalchemy import func, select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.referral import Referral

logger = logging.getLogger(__name__)


class ReferralRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_referral(self, referrer_id: int, referred_id: int) -> None:
        try:
            if referrer_id == referred_id:
                logger.warning(f"Referrer ID and referred ID are the same: {referrer_id}")
                raise ValueError("User cannot refer themselves.")

            existing_referral = await self.session.scalar(
                select(Referral).where(
                    Referral.referrer_id == referrer_id,
                    Referral.referred_id == referred_id
                )
            )
            if existing_referral:
                logger.warning(f"Referral from {referrer_id} to {referred_id} already exists.")
                return

            new_referral = Referral(referrer_id=referrer_id, referred_id=referred_id)
            self.session.add(new_referral)
            await self.session.commit()
        except DatabaseError as e:
            await self.session.rollback()
            logger.error(f"Database error occurred while adding referral: {e}")
            raise

    async def get_referral_count(self, referrer_id: int) -> int:
        try:
            count = await self.session.scalar(
                select(func.count()).select_from(Referral).where(Referral.referrer_id == referrer_id)
            )
            return count or 0
        except DatabaseError as e:
            logger.error(f"Database error occurred while counting referrals for referrer_id={referrer_id}: {e}")
            return 0