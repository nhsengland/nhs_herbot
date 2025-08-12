"""
Simple SQL Server database interaction module.
"""

from pathlib import Path
from typing import Dict, Optional, Union

from loguru import logger
import pandas as pd
import pyodbc

from nhs_herbot.errors import DatabaseConnectionError, InvalidParametersError, SQLExecutionError


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
        self._connection: Optional[pyodbc.Connection] = None

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

    def write_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str = "dbo",
        if_exists: str = "fail",
        index: bool = False,
        method: Optional[str] = None,
        chunksize: Optional[int] = None,
    ) -> None:
        """
        Write a pandas DataFrame to a SQL Server table.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to write
        table_name : str
            Name of the target table
        schema : str, optional
            Database schema, by default "dbo"
        if_exists : str, optional
            How to behave if table exists {'fail', 'replace', 'append'}, by default "fail"
        index : bool, optional
            Whether to write DataFrame index as a column, by default False
        method : str, optional
            Method to use for writing {'multi', None, callable}, by default None
        chunksize : int, optional
            Number of rows to write at a time, by default None

        Raises
        ------
        InvalidParametersError
            If parameters are invalid
        SQLExecutionError
            If write operation fails
        """
        if df is None or df.empty:
            raise InvalidParametersError("DataFrame cannot be None or empty")

        if not table_name or not table_name.strip():
            raise InvalidParametersError("Table name cannot be empty")

        if if_exists not in ["fail", "replace", "append"]:
            raise InvalidParametersError("if_exists must be 'fail', 'replace', or 'append'")

        valid_methods = [None, "multi"]
        if method is not None and method not in valid_methods:
            raise InvalidParametersError("method must be None or 'multi'")

        try:
            full_table_name = f"{schema}.{table_name}"
            logger.info(f"Writing DataFrame to table {full_table_name}")
            df.to_sql(
                name=table_name,
                con=self._connection,
                schema=schema,
                if_exists=if_exists,  # type: ignore
                index=index,
                method=method,  # type: ignore
                chunksize=chunksize,
            )
            logger.info(f"Successfully wrote {len(df)} rows to {full_table_name}")
        except Exception as e:
            error_msg = f"Failed to write DataFrame to {schema}.{table_name}: {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def execute_non_query(self, sql: str, params: Optional[Dict[str, str]] = None) -> int:
        """
        Execute a non-query SQL statement (INSERT, UPDATE, DELETE, etc.).

        Parameters
        ----------
        sql : str
            SQL statement to execute
        params : dict, optional
            Optional parameters for SQL statement, by default None

        Returns
        -------
        int
            Number of rows affected

        Raises
        ------
        InvalidParametersError
            If SQL is empty
        SQLExecutionError
            If execution fails
        """
        if not sql or not sql.strip():
            raise InvalidParametersError("SQL statement cannot be empty")

        if self._connection is None:
            raise SQLExecutionError("No database connection available")

        try:
            logger.info("Executing non-query SQL statement")
            cursor = self._connection.cursor()

            # Format SQL with parameters if provided
            if params:
                logger.info(f"Applying {len(params)} parameter replacements")
                formatted_sql = sql.format(**params)
            else:
                formatted_sql = sql

            cursor.execute(formatted_sql)
            rowcount = cursor.rowcount
            self._connection.commit()
            cursor.close()

            logger.info(f"Non-query executed successfully, {rowcount} rows affected")
            return rowcount

        except Exception as e:
            try:
                if self._connection:
                    self._connection.rollback()
                    logger.warning("Transaction rolled back due to error")
            except Exception:
                logger.error("Failed to rollback transaction")
            error_msg = f"Failed to execute non-query: {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def execute_non_query_from_file(
        self, file_path: Union[str, Path], params: Optional[Dict[str, str]] = None
    ) -> int:
        """
        Execute a non-query SQL statement from a file.

        Parameters
        ----------
        file_path : Union[str, Path]
            Path to SQL file
        params : dict, optional
            Optional parameters for SQL statement, by default None

        Returns
        -------
        int
            Number of rows affected

        Raises
        ------
        InvalidParametersError
            If file doesn't exist
        SQLExecutionError
            If execution fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise InvalidParametersError(f"SQL file not found: {file_path}")

        if not file_path.is_file():
            raise InvalidParametersError(f"Path is not a file: {file_path}")

        try:
            logger.info(f"Reading non-query SQL from file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                sql_content = file.read()

            return self.execute_non_query(sql_content, params)

        except FileNotFoundError as e:
            raise InvalidParametersError(f"SQL file not found: {file_path}") from e
        except Exception as e:
            if isinstance(e, (InvalidParametersError, SQLExecutionError)):
                raise
            error_msg = f"Failed to execute SQL from file '{file_path}': {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def bulk_insert(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str = "dbo",
        batch_size: int = 1000,
    ) -> None:
        """
        Perform bulk insert using SQL Server's bulk insert capabilities.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to insert
        table_name : str
            Target table name
        schema : str, optional
            Database schema, by default "dbo"
        batch_size : int, optional
            Number of rows to insert per batch, by default 1000

        Raises
        ------
        InvalidParametersError
            If parameters are invalid
        SQLExecutionError
            If bulk insert fails
        """
        if df is None or df.empty:
            raise InvalidParametersError("DataFrame cannot be None or empty")

        if not table_name or not table_name.strip():
            raise InvalidParametersError("Table name cannot be empty")

        if batch_size <= 0:
            raise InvalidParametersError("Batch size must be positive")

        try:
            full_table_name = f"{schema}.{table_name}"
            logger.info(f"Starting bulk insert to {full_table_name} with batch size {batch_size}")

            # Use pandas to_sql with method='multi' for better performance
            df.to_sql(
                name=table_name,
                con=self._connection,
                schema=schema,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=batch_size,
            )

            logger.info(f"Bulk insert completed: {len(df)} rows inserted to {full_table_name}")

        except Exception as e:
            error_msg = f"Bulk insert failed for {schema}.{table_name}: {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def create_table_from_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: str = "dbo",
        dtype_mapping: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Create a new table based on DataFrame structure.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to base table structure on
        table_name : str
            Name of table to create
        schema : str, optional
            Database schema, by default "dbo"
        dtype_mapping : dict, optional
            Optional mapping of column names to SQL types, by default None

        Raises
        ------
        InvalidParametersError
            If parameters are invalid
        SQLExecutionError
            If table creation fails
        """
        if df is None or df.empty:
            raise InvalidParametersError("DataFrame cannot be None or empty")

        if not table_name or not table_name.strip():
            raise InvalidParametersError("Table name cannot be empty")

        try:
            full_table_name = f"{schema}.{table_name}"
            logger.info(f"Creating table {full_table_name} from DataFrame structure")

            # Write just the structure (0 rows) to create the table
            empty_df = df.iloc[0:0].copy()

            # Apply dtype mapping if provided
            if dtype_mapping:
                logger.info(f"Applying {len(dtype_mapping)} data type mappings")
                empty_df = empty_df.astype(dtype_mapping)

            empty_df.to_sql(
                name=table_name,
                con=self._connection,
                schema=schema,
                if_exists="fail",
                index=False,
            )

            logger.info(f"Table {full_table_name} created successfully")

        except Exception as e:
            error_msg = f"Failed to create table {schema}.{table_name}: {str(e)}"
            raise SQLExecutionError(error_msg) from e

    def table_exists(self, table_name: str, schema: str = "dbo") -> bool:
        """
        Check if a table exists in the database.

        Parameters
        ----------
        table_name : str
            Name of table to check
        schema : str, optional
            Database schema, by default "dbo"

        Returns
        -------
        bool
            True if table exists, False otherwise

        Raises
        ------
        InvalidParametersError
            If parameters are invalid
        SQLExecutionError
            If check fails
        """
        if not table_name or not table_name.strip():
            raise InvalidParametersError("Table name cannot be empty")

        if self._connection is None:
            raise SQLExecutionError("No database connection available")

        try:
            logger.info(f"Checking if table {schema}.{table_name} exists")
            query = """
            SELECT COUNT(*) as table_count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            """

            cursor = self._connection.cursor()
            cursor.execute(query, (schema, table_name))
            result = cursor.fetchone()
            cursor.close()

            if result is None:
                return False

            exists = result[0] > 0
            logger.info(f"Table {schema}.{table_name} exists: {exists}")
            return exists

        except Exception as e:
            error_msg = f"Failed to check if table {schema}.{table_name} exists: {str(e)}"
            raise SQLExecutionError(error_msg) from e
