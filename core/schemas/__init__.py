from core.schemas.game_tasks import GameTaskResponsePaginateSchema, GameTaskSchema
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
    'GameTaskSchema',
    'PromoCodeReceiveSchema',
    'RemainingTimeSchema',
    'UserActivitySchema',
    'ReferralAddingSchema',
    'UserCreateSchema',
    'UserKeyGenerationSchema',
    'UserProgressSchema',
    'UserProgressDataSchema'
]
