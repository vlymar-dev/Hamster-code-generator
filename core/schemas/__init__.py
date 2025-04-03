from core.schemas.game_tasks import GameTaskResponsePaginateSchema, GameTaskResponseSchema
from core.schemas.promo_code import PromoCodeReceiveSchema
from core.schemas.referral import ReferralAddingSchema
from core.schemas.user import (
    RemainingTimeSchema,
    UserActivitySchema,
    UserCreateSchema,
    UserKeyGenerationSchema,
    UserProgressDataSchema,
    UserProgressSchema,
)

__all__ = [
    'GameTaskResponsePaginateSchema',
    'GameTaskResponseSchema',
    'PromoCodeReceiveSchema',
    'RemainingTimeSchema',
    'UserActivitySchema',
    'ReferralAddingSchema',
    'UserCreateSchema',
    'UserKeyGenerationSchema',
    'UserProgressSchema',
    'UserProgressDataSchema'
]
