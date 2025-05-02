from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def mock_config():
    with mock.patch('infrastructure.config') as mock_config:
        mock_config.PROD_MODE = False
        yield mock_config


@pytest.fixture
def mock_base_dir():
    with mock.patch('infrastructure.BASE_DIR', Path('/mock/base/dir')):
        yield
