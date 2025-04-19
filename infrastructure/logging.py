import logging
from logging.handlers import TimedRotatingFileHandler

from infrastructure import BASE_DIR, config


def setup_logging(
    app_name: str = 'my_app',
    enable_console_logs: bool = None,
    root_log_level: int = logging.DEBUG,
    file_log_level: int = None,
    console_log_level: int = logging.DEBUG,
) -> None:
    """Configure application-wide logging with flexible level settings.

    Creates rotating log files and optional console output with separate level controls.
    Log directory structure: ./logs/{app_name}/{app_name}.log

    Args:
        app_name (str): Application name for log directory and filenames.
            Default: 'my_app'.
        enable_console_logs (bool): Enable console logging.
            Default: `not PROD_MODE` (True in development, False in production).
        root_log_level (int): Root logger level (DEBUG/INFO/WARNING/ERROR/CRITICAL).
            Default: DEBUG.
        file_log_level (int): Minimum level for file logging.
            Default: INFO in production, DEBUG in development.
        console_log_level (int): Minimum level for console logging.
            Default: DEBUG.

    Example:
        # Production setup (no console logs, file level=INFO)
        >>> setup_logging(
        >>>     app_name='my_prod_app',
        >>>     enable_console_logs=False,
        >>>     file_log_level=logging.INFO
        >>> )

        # Development setup (console logs enabled, file level=DEBUG)
        >>> setup_logging(app_name='my_dev_app')
    """
    # Set default values
    if enable_console_logs is None:
        enable_console_logs = not config.PROD_MODE
    if file_log_level is None:
        file_log_level = logging.INFO if config.PROD_MODE else logging.DEBUG

    log_dir = BASE_DIR / 'var' / 'logs' / app_name
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise RuntimeError(f'Cannot create log directory: {log_dir}') from e

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)', datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=log_dir / f'{app_name}.log', when='midnight', backupCount=30, encoding='utf-8', utc=True
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_log_level)
    file_handler._custom_handler = True

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(root_log_level)

    # Console handler with separate level
    console_handler = None
    if enable_console_logs:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(console_log_level)
        console_handler._custom_handler = True

    # Clear previous handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        if getattr(handler, '_custom_handler', False):
            handler.close()
            root_logger.removeHandler(handler)

    root_logger.addHandler(file_handler)
    if console_handler:
        root_logger.addHandler(console_handler)

    root_logger.info(
        f'Logging initialized for {app_name} '
        f'(file level: {logging.getLevelName(file_log_level)}, '
        f'console level: {logging.getLevelName(console_log_level)})'
    )
