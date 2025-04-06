from core.services.admin_panel import AdminPanelService
from core.services.game_task import GameTaskService
from core.services.progres import ProgressService
from core.services.promo_code import PromoCodeService
from core.services.user import UserService

progres_service = ProgressService()

__all__ = ['AdminPanelService', 'GameTaskService', 'progres_service', 'PromoCodeService', 'UserService']
