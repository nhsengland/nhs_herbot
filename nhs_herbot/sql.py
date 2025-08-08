"""
Simple SQL Server database interaction module.
"""

from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
import pyodbc
from loguru import logger

from nhs_herbot.errors import (
    DatabaseConnectionError,
    InvalidParametersError,
    SQLExecutionError,
)


class SQLServer:
    """
    Simple class for SQL Server database operations.

    Parameters
    ----------
    server : str
        The SQL Server instance name
    uid : str
        User ID for authentication
    database : str
        Database name to connect to
    driver : str, optional
        ODBC driver version, by default "ODBC Driver 17 for SQL Server"
    timeout : int, optional
        Connection timeout in seconds, by default 30

    Examples
    --------
    >>> sql = SQLServer("myserver", "myuser", "mydatabase")
    >>> df = sql.query("SELECT * FROM table")
    >>> df2 = sql.query_from_file("query.sql", {"param": "value"})
    """

    def __init__(
        self,
        server: str,
        uid: str,
        database: str,
        driver: str = "ODBC Driver 17 for SQL Server",
        timeout: int = 30,
    ):
        self.server = server
        self.uid = uid
        self.database = database
        self.driver = driver
        self.timeout = timeout
        self._connection = None

        # Validate inputs
        if not all([server, uid, database]):
            raise InvalidParametersError("Server, UID, and database must all be provided")

        if timeout <= 0:
            raise InvalidParametersError("Timeout must be positive")

        self._connect()

    def _connect(self) -> None:
        """Establish database connection."""
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"UID={self.uid};"
            f"DATABASE={self.database};"
            f"TIMEOUT={self.timeout};"
            "Authentication=ActiveDirectoryInteractive;"
        )

        try:
            logger.info(f"Connecting to database '{self.database}' on server '{self.server}'")
            self._connection = pyodbc.connect(conn_str, timeout=self.timeout)
            logger.info("Database connection successful")
        except pyodbc.Error as e:
            error_msg = f"Failed to connect to database '{self.database}' on server '{self.server}': {str(e)}"
            raise DatabaseConnectionError(error_msg) from e

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.

        Parameters
        ----------
        sql : str
            SQL query to execute

        Returns
        -------
        pd.DataFrame
            Query results

        Raises
        ------
        SQLExecutionError
            If query execution fails
        """
        if not sql.strip():
            raise InvalidParametersError("SQL query cannot be empty")

        try:
            logger.info("Executing SQL query")
            df = pd.read_sql(sql, self._connection)
            logger.info(
                f"Query executed successfully, returned {len(df)} rows and {len(df.columns)} columns"
            )
            return df
        except Exception as e:
            error_msg = f"Failed to execute SQL query: {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def query_from_file(
        self, file_path: Union[str, Path], replacements: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Load SQL from file, apply replacements, and execute.

        Parameters
        ----------
        file_path : Union[str, Path]
            Path to SQL file
        replacements : Optional[Dict[str, str]], optional
            Dictionary of replacements to apply using str.format(), by default None

        Returns
        -------
        pd.DataFrame
            Query results

        Raises
        ------
        InvalidParametersError
            If file doesn't exist or other parameter issues
        SQLExecutionError
            If file reading or query execution fails
        """
        if replacements is None:
            replacements = {}

        file_path = Path(file_path)

        if not file_path.exists():
            raise InvalidParametersError(f"SQL file not found: {file_path}")

        if not file_path.is_file():
            raise InvalidParametersError(f"Path is not a file: {file_path}")

        try:
            logger.info(f"Reading SQL query from file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                sql = file.read()

            # Apply replacements using format
            if replacements:
                logger.info(f"Applying {len(replacements)} replacements to SQL query")
                sql = sql.format(**replacements)

            return self.query(sql)

        except FileNotFoundError as e:
            raise InvalidParametersError(f"SQL file not found: {file_path}") from e
        except Exception as e:
            error_msg = f"Failed to read or execute SQL file '{file_path}': {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
