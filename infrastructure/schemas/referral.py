from pydantic import BaseModel


class ReferralAddingSchema(BaseModel):
    referrer_id: int
    referred_id: int
