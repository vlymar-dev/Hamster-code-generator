import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(
        app_name: str = 'my_app',
        console_logs: bool = True,
        log_level: int = logging.DEBUG,
        file_log_level: int = logging.INFO,
        console_log_level: int = logging.DEBUG
) -> None:
    """Configure application-wide logging with flexible level settings.

    Creates rotating log files and optional console output with separate level controls.
    Log directory structure: ./logs/{app_name}/{app_name}.log

    Args:
        app_name (str): Application name for log directory and filenames.
            Default: 'default'.
        console_logs (bool): Enable console logging. Default: True.
        log_level (int): Root logger level (DEBUG/INFO/WARNING/ERROR/CRITICAL).
            Default: DEBUG.
        file_log_level (int): Minimum level for file logging. Default: INFO.
        console_log_level (int): Minimum level for console logging. Default: DEBUG.

    Example:
        >>> setup_logging(
        >>>     app_name='my_app',
        >>>     console_logs=False,
        >>>     log_level=logging.INFO,
        >>>     file_log_level=logging.WARNING
        >>> )
    """
    log_dir = Path(__file__).parent / 'logs' / app_name
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
    )

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=log_dir / f'{app_name}.log',
        when='midnight',
        backupCount=30,
        encoding='utf-8',
        utc=True
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_log_level)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear previous handlers to avoid duplicate logs
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.addHandler(file_handler)

    # Console handler with separate level
    if console_logs:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(console_log_level)
        root_logger.addHandler(console_handler)

    root_logger.info(f'Logging initialized for {app_name} '
                     f'(file level: {logging.getLevelName(file_log_level)}, '
                     f'console level: {logging.getLevelName(console_log_level)})')
