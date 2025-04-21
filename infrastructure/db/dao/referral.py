import logging

from infrastructure.db.dao.base import BaseDAO
from infrastructure.db.models import Referral

logger = logging.getLogger(__name__)


class ReferralDAO(BaseDAO[Referral]):
    """DAO for referral management."""

    model = Referral
