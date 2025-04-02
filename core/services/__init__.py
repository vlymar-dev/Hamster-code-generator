from core.services.progres import ProgressService
from core.services.promo_code import PromoCodeService
from core.services.user import UserService

progres_service = ProgressService()

__all__ = ['progres_service', 'PromoCodeService', 'UserService']
