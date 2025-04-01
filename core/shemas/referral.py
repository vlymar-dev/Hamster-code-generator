from pydantic import BaseModel


class ReferralCreateSchema(BaseModel):
    referrer_id: int
    referred_id: int
