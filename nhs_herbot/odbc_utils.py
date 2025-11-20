"""
ODBC driver detection and validation utilities.

Provides intelligent detection of ODBC setup issues with actionable error messages.
"""

import platform
from typing import Optional

from loguru import logger

# Lazy import of pyodbc with error capture
_pyodbc = None
_pyodbc_import_error: Optional[ImportError] = None

try:
    import pyodbc

    _pyodbc = pyodbc
except ImportError as e:
    _pyodbc_import_error = e


class ODBCDriverDetector:
    """Detects and validates ODBC driver setup."""

    @staticmethod
    def get_pyodbc():
        """Get pyodbc module or None if unavailable."""
        return _pyodbc

    @staticmethod
    def check_pyodbc_package() -> None:
        """
        Verify pyodbc package is available.

        Raises
        ------
        ImportError
            If pyodbc package is not installed with installation instructions.
        """
        if _pyodbc is None and _pyodbc_import_error and "libodbc" not in str(_pyodbc_import_error):
            raise ImportError(
                "pyodbc is required for SQL Server functionality.\n"
                "Install with: uv pip install nhs-herbot[sql]"
            )

    @staticmethod
    def check_system_libraries() -> None:
        """
        Verify ODBC system libraries are available.

        Raises
        ------
        Exception
            If system ODBC libraries are missing with OS-specific installation instructions.
        """
        from nhs_herbot.errors import DatabaseConnectionError

        if _pyodbc is None and _pyodbc_import_error and "libodbc" in str(_pyodbc_import_error):
            system = platform.system().lower()

            instructions = {
                "linux": (
                    "Install system dependencies:\n"
                    "  Ubuntu/Debian: sudo apt-get install unixodbc unixodbc-dev\n"
                    "  RHEL/CentOS/Fedora: sudo yum install unixODBC unixODBC-devel"
                ),
                "darwin": ("Install with Homebrew:\n  brew install unixodbc"),
            }

            instruction = instructions.get(
                system, "Please install ODBC system libraries for your OS."
            )
            error_msg = (
                f"ODBC system libraries not found. pyodbc is installed but cannot load libodbc.so.\n\n"
                f"{instruction}\n\n"
                f"Original error: {_pyodbc_import_error}"
            )
            raise DatabaseConnectionError(error_msg) from _pyodbc_import_error

    @staticmethod
    def get_available_drivers() -> list[str]:
        """
        Get list of registered ODBC drivers.

        Returns
        -------
        List[str]
            List of available ODBC driver names.

        Raises
        ------
        Exception
            If cannot access ODBC driver list with troubleshooting steps.
        """
        from nhs_herbot.errors import DatabaseConnectionError

        if _pyodbc is None:
            return []

        try:
            return _pyodbc.drivers()
        except Exception as e:
            system = platform.system().lower()

            instructions = {
                "linux": (
                    "Install system dependencies:\n"
                    "  Ubuntu/Debian: sudo apt-get install unixodbc-dev\n"
                    "  RHEL/CentOS/Fedora: sudo yum install unixODBC-devel"
                ),
                "darwin": ("Install with Homebrew:\n  brew install unixodbc"),
                "windows": "Windows should have ODBC pre-installed. Check ODBC Data Source Administrator.",
            }

            instruction = instructions.get(system, "Please configure ODBC for your OS.")
            error_msg = (
                f"Cannot access ODBC drivers. System ODBC configuration may be incomplete.\n\n"
                f"{instruction}\n\n"
                f"Original error: {e}"
            )
            raise DatabaseConnectionError(error_msg) from e

    @staticmethod
    def check_drivers_available(drivers: list[str]) -> None:
        """
        Verify at least one ODBC driver is registered.

        Parameters
        ----------
        drivers : List[str]
            List of available drivers from get_available_drivers().

        Raises
        ------
        Exception
            If no drivers are registered with installation guidance.
        """
        from nhs_herbot.errors import DatabaseConnectionError

        if not drivers:
            error_msg = (
                "No ODBC drivers registered. Install Microsoft ODBC Driver or FreeTDS:\n\n"
                "Microsoft ODBC Driver (recommended):\n"
                "  https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server\n\n"
                "FreeTDS (open source alternative):\n"
                "  Ubuntu/Debian: sudo apt-get install tdsodbc\n"
                "  RHEL/CentOS/Fedora: sudo yum install freetds"
            )
            raise DatabaseConnectionError(error_msg)

    @staticmethod
    def validate_sql_server_drivers(drivers: list[str]) -> None:
        """
        Check for SQL Server compatible drivers and log warnings if needed.

        Parameters
        ----------
        drivers : List[str]
            List of available ODBC drivers.
        """
        sql_server_drivers = [d for d in drivers if "SQL Server" in d]
        freetds_drivers = [d for d in drivers if "FreeTDS" in d or "TDS" in d]

        if not sql_server_drivers and not freetds_drivers:
            logger.warning(
                f"No SQL Server compatible drivers found. Available: {', '.join(drivers)}\n"
                "Install Microsoft ODBC Driver or FreeTDS for SQL Server connectivity."
            )
        elif not sql_server_drivers and freetds_drivers:
            logger.warning(
                f"Using FreeTDS ({', '.join(freetds_drivers)}). "
                "This works but Microsoft's official driver is recommended.\n"
                "To install: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/"
                "installing-the-microsoft-odbc-driver-for-sql-server"
            )


def validate_odbc_setup() -> None:
    """
    Comprehensive ODBC setup validation with helpful error messages.

    Checks for:
    - pyodbc Python package installation
    - System ODBC libraries (libodbc.so on Linux)
    - Registered ODBC drivers
    - SQL Server compatible drivers (Microsoft or FreeTDS)

    Raises
    ------
    ImportError
        If pyodbc package is not installed.
    DatabaseConnectionError
        If ODBC system libraries or drivers are missing.
    """
    detector = ODBCDriverDetector()

    # Step 1: Check pyodbc package
    detector.check_pyodbc_package()

    # Step 2: Check system libraries
    detector.check_system_libraries()

    # Step 3: Get available drivers
    drivers = detector.get_available_drivers()

    # Step 4: Verify at least one driver exists
    detector.check_drivers_available(drivers)

    # Step 5: Validate SQL Server compatibility
    detector.validate_sql_server_drivers(drivers)
