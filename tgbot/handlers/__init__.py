from . import commands, callback_queries


def register_handlers(dp):
    commands.register_commands_handler(dp)
    callback_queries.register_callback_queries_handler(dp)
