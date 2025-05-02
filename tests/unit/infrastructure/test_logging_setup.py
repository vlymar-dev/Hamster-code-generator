from pathlib import Path
from unittest import mock

from infrastructure.logging import setup_logging


@mock.patch('infrastructure.logging.TimedRotatingFileHandler')
@mock.patch('infrastructure.logging.logging.getLogger')
def test_setup_logging_no_file_creation(mock_get_logger, mock_file_handler_cls, mock_config, mock_base_dir):
    mock_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_file_handler = mock.MagicMock()
    mock_file_handler_cls.return_value = mock_file_handler

    with mock.patch.object(Path, 'mkdir') as mock_mkdir:
        setup_logging(app_name='test_app')

        mock_mkdir.assert_called_once()
        mock_file_handler_cls.assert_called_once()
        mock_logger.addHandler.assert_any_call(mock_file_handler)
