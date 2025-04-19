from infrastructure.services.admin_panel import AdminPanelService
from infrastructure.services.cache import CacheService
from infrastructure.services.game_task import GameTaskService
from infrastructure.services.progres import ProgressService
from infrastructure.services.promo_code import PromoCodeService
from infrastructure.services.user import UserCacheService, UserService

progres_service = ProgressService()

__all__ = [
    'AdminPanelService',
    'CacheService',
    'GameTaskService',
    'progres_service',
    'PromoCodeService',
    'UserCacheService',
    'UserService',
]
