from core.services.game_task import GameTaskService
from core.services.progres import ProgressService
from core.services.promo_code import PromoCodeService
from core.services.user import UserService

progres_service = ProgressService()

__all__ = ['GameTaskService', 'progres_service', 'PromoCodeService', 'UserService']
