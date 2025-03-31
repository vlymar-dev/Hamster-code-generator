from bot.handlers.commands import commands_router
from bot.handlers.donations.donations import donations_router
from bot.handlers.donations.refund import refund_router
from bot.handlers.games_keys import games_keys_router
from bot.handlers.info import info_router
from bot.handlers.main_menu import main_menu_router
from bot.handlers.progress import progress_router
from bot.handlers.referral_links import referral_links_router
from bot.handlers.settings import settings_router

ROUTERS = [
    commands_router,
    donations_router,
    refund_router,
    games_keys_router,
    info_router,
    main_menu_router,
    progress_router,
    referral_links_router,
    settings_router
]

__all__ = ['ROUTERS']
