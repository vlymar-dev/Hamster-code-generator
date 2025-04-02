from sqlalchemy.ext.asyncio import AsyncSession

from core.shemas import UserCreateSchema
from core.shemas.referral import ReferralAddingSchema
from db.repositories import ReferralsRepository, UserRepository


class UserService:

    @staticmethod
    async def user_registration(session: AsyncSession, user_id: int, user: UserCreateSchema) -> bool:
        exists_user: bool = await UserRepository.check_user_exists(session, user_id)
        if exists_user:
            return False

        await UserRepository.add_user(session, user)
        return True

    @staticmethod
    async def referral_adding(session: AsyncSession, referrer_id: int, referred_id: int) -> int | None:
        if not await UserRepository.check_user_exists(session, referrer_id):
            return None

        referrals_data = ReferralAddingSchema(referrer_id=referrer_id, referred_id=referred_id)
        await ReferralsRepository.add_referral(session, referrals_data)
        return referrer_id
