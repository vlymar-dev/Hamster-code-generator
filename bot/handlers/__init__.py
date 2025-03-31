from bot.handlers.commands import commands_router
from bot.handlers.game_center import game_center_router
from bot.handlers.info import info_router
from bot.handlers.main_menu import main_menu_router
from bot.handlers.progress import progress_router
from bot.handlers.settings import settings_router

ROUTERS = [
    commands_router,
    game_center_router,
    info_router,
    main_menu_router,
    progress_router,
    settings_router
]

__all__ = ['ROUTERS']
