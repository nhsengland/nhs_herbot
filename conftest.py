"""
This module contains fixtures that are used by the test modules in the tests/ directory.
"""

from typing import Any, Dict, Literal
import warnings
import pandas as pd
import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*platformdirs.*")

Logger = Any

MockLoggerDict = Dict[
    Literal["info"]
    | Literal["error"]
    | Literal["warning"]
    | Literal["success"]
    | Literal["debug"],
    Logger,
]


@pytest.fixture
def mock_info(mocker):
    """
    Fixture to mock the loguru.logger.info method
    """
    return mocker.patch("loguru.logger.info")


@pytest.fixture
def mock_error(mocker):
    """
    Fixture to mock the loguru.logger.error method
    """
    return mocker.patch("loguru.logger.error")


@pytest.fixture
def mock_warning(mocker):
    """
    Fixture to mock the loguru.logger.warning method
    """
    return mocker.patch("loguru.logger.warning")


@pytest.fixture
def mock_success(mocker):
    """
    Fixture to mock the loguru.logger.success method
    """
    return mocker.patch("loguru.logger.success")


@pytest.fixture
def mock_debug(mocker):
    """
    Fixture to mock the loguru.logger.debug method
    """
    return mocker.patch("loguru.logger.debug")


@pytest.fixture(autouse=True)
def mock_log_levels(
    mock_info, mock_error, mock_warning, mock_success, mock_debug
) -> MockLoggerDict:
    """
    Fixture to mock the loguru.logger methods:
    - info
    - error
    - warning
    - success
    - debug
    """
    return {
        "info": mock_info,
        "error": mock_error,
        "warning": mock_warning,
        "success": mock_success,
        "debug": mock_debug,
    }


@pytest.fixture
def empty_df():
    """
    Fixture to return an empty DataFrame
    """
    return pd.DataFrame()
