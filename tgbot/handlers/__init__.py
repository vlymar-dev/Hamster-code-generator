from . import callback_queries, commands
from .admin_panel import admin_handlers, announcements_handlers
from .donation import donation_handlers, refund_command


def register_handlers(dp):
    commands.register_commands_handler(dp)
    callback_queries.register_callback_queries_handler(dp)
    donation_handlers.register_donation_handlers(dp)
    refund_command.register_refund_command_handler(dp)
    admin_handlers.register_admin_panel_handlers(dp)
    announcements_handlers.register_announcements_handlers(dp)
