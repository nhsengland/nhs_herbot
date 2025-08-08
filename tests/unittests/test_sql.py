"""
Tests for nhs_herbot/sql.py SQLServer class
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import pyodbc

from nhs_herbot.sql import SQLServer
from nhs_herbot.errors import DatabaseConnectionError, InvalidParametersError, SQLExecutionError


class TestSQLServer:
    """Tests for SQLServer class"""

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_init_success(self, mock_connect):
        """Test successful initialization"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        sql = SQLServer("server", "user", "database")

        assert sql.server == "server"
        assert sql.uid == "user"
        assert sql.database == "database"
        assert sql.driver == "ODBC Driver 17 for SQL Server"
        assert sql.timeout == 30
        mock_connect.assert_called_once()

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_init_custom_driver(self, mock_connect):
        """Test initialization with custom driver"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        sql = SQLServer("server", "user", "database", driver="ODBC Driver 18 for SQL Server")

        assert sql.driver == "ODBC Driver 18 for SQL Server"

    def test_init_invalid_parameters(self):
        """Test initialization with invalid parameters"""
        with pytest.raises(InvalidParametersError):
            SQLServer("", "user", "database")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "", "database")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "user", "")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "user", "database", timeout=-1)

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_init_connection_failure(self, mock_connect):
        """Test connection failure during initialization"""
        mock_connect.side_effect = pyodbc.Error("Connection failed")

        with pytest.raises(DatabaseConnectionError):
            SQLServer("server", "user", "database")

    @patch("nhs_herbot.sql.pyodbc.connect")
    @patch("nhs_herbot.sql.pd.read_sql")
    def test_query_success(self, mock_read_sql, mock_connect):
        """Test successful query execution"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_sql.return_value = mock_df

        sql = SQLServer("server", "user", "database")
        result = sql.query("SELECT * FROM test")

        assert result.equals(mock_df)
        mock_read_sql.assert_called_once_with("SELECT * FROM test", mock_conn)

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_query_empty_sql(self, mock_connect):
        """Test query with empty SQL"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.query("")

    @patch("nhs_herbot.sql.pyodbc.connect")
    @patch("nhs_herbot.sql.pd.read_sql")
    def test_query_execution_error(self, mock_read_sql, mock_connect):
        """Test query execution error"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        mock_read_sql.side_effect = Exception("SQL error")

        sql = SQLServer("server", "user", "database")

        with pytest.raises(SQLExecutionError):
            sql.query("SELECT * FROM test")

    @patch("nhs_herbot.sql.pyodbc.connect")
    @patch("nhs_herbot.sql.pd.read_sql")
    def test_query_from_file_success(self, mock_read_sql, mock_connect):
        """Test successful query from file"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mock_read_sql.return_value = mock_df

        sql_content = "SELECT * FROM {table_name}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            temp_path = f.name

        try:
            sql = SQLServer("server", "user", "database")
            result = sql.query_from_file(temp_path, {"table_name": "test_table"})

            assert result.equals(mock_df)
            mock_read_sql.assert_called_once_with("SELECT * FROM test_table", mock_conn)
        finally:
            Path(temp_path).unlink()

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_query_from_file_not_found(self, mock_connect):
        """Test query from non-existent file"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError) as exc_info:
            sql.query_from_file("/nonexistent/file.sql")

        assert "SQL file not found" in str(exc_info.value)

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_close_connection(self, mock_connect):
        """Test closing connection"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        sql = SQLServer("server", "user", "database")
        sql.close()

        mock_conn.close.assert_called_once()

    @patch("nhs_herbot.sql.pyodbc.connect")
    def test_context_manager(self, mock_connect):
        """Test context manager usage"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        with SQLServer("server", "user", "database") as sql:
            assert isinstance(sql, SQLServer)

        mock_conn.close.assert_called_once()
