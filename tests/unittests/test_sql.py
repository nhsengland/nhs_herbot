"""
Tests for nhs_herbot/sql.py SQLServer class
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
import pyodbc

from nhs_herbot.sql import SQLServer
from nhs_herbot.errors import DatabaseConnectionError, InvalidParametersError, SQLExecutionError


class TestSQLServer:
    """Tests for SQLServer class"""

    def test_init_success(self, mocker):
        """Test successful initialization"""
        mock_conn = mocker.Mock()
        mock_connect = mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        assert sql.server == "server"
        assert sql.uid == "user"
        assert sql.database == "database"
        assert sql.driver == "ODBC Driver 17 for SQL Server"
        assert sql.timeout == 30
        mock_connect.assert_called_once()

    def test_init_custom_driver(self, mocker):
        """Test initialization with custom driver"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

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

    def test_init_connection_failure(self, mocker):
        """Test connection failure during initialization"""
        mocker.patch(
            "nhs_herbot.sql.pyodbc.connect", side_effect=pyodbc.Error("Connection failed")
        )

        with pytest.raises(DatabaseConnectionError):
            SQLServer("server", "user", "database")

    def test_query_success(self, mocker):
        """Test successful query execution"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("nhs_herbot.sql.pd.read_sql", return_value=mock_df)

        sql = SQLServer("server", "user", "database")
        result = sql.query("SELECT * FROM test")

        assert result.equals(mock_df)

    def test_query_empty_sql(self, mocker):
        """Test query with empty SQL"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.query("")

    def test_query_execution_error(self, mocker):
        """Test query execution error"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)
        mocker.patch("nhs_herbot.sql.pd.read_sql", side_effect=Exception("SQL error"))

        sql = SQLServer("server", "user", "database")

        with pytest.raises(SQLExecutionError):
            sql.query("SELECT * FROM test")

    def test_query_from_file_success(self, mocker):
        """Test successful query from file"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mocker.patch("nhs_herbot.sql.pd.read_sql", return_value=mock_df)

        sql_content = "SELECT * FROM {table_name}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            temp_path = f.name

        try:
            sql = SQLServer("server", "user", "database")
            result = sql.query_from_file(temp_path, {"table_name": "test_table"})

            assert result.equals(mock_df)
        finally:
            Path(temp_path).unlink()

    def test_query_from_file_not_found(self, mocker):
        """Test query from non-existent file"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError) as exc_info:
            sql.query_from_file("/nonexistent/file.sql")

        assert "SQL file not found" in str(exc_info.value)

    def test_close_connection(self, mocker):
        """Test closing connection"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        sql.close()

        mock_conn.close.assert_called_once()

    def test_context_manager(self, mocker):
        """Test context manager usage"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        with SQLServer("server", "user", "database") as sql:
            assert isinstance(sql, SQLServer)

        mock_conn.close.assert_called_once()

    def test_write_dataframe_success(self, mocker):
        """Test successful DataFrame write"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_to_sql = mocker.patch.object(df, "to_sql")

        sql = SQLServer("server", "user", "database")
        sql.write_dataframe(df, "test_table")

        mock_to_sql.assert_called_once_with(
            name="test_table",
            con=mock_conn,
            schema="dbo",
            if_exists="fail",
            index=False,
            method=None,
            chunksize=None,
        )

    def test_write_dataframe_invalid_params(self, mocker):
        """Test write DataFrame with invalid parameters"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        # Test empty DataFrame
        empty_df = pd.DataFrame()
        with pytest.raises(InvalidParametersError):
            sql.write_dataframe(empty_df, "test_table")

        # Test None DataFrame
        with pytest.raises(InvalidParametersError):
            sql.write_dataframe(None, "test_table")  # type: ignore

        # Test empty table name
        df = pd.DataFrame({"col1": [1, 2]})
        with pytest.raises(InvalidParametersError):
            sql.write_dataframe(df, "")

        # Test invalid if_exists
        with pytest.raises(InvalidParametersError):
            sql.write_dataframe(df, "test_table", if_exists="invalid")

        # Test invalid method
        with pytest.raises(InvalidParametersError):
            sql.write_dataframe(df, "test_table", method="invalid")

    def test_execute_non_query_success(self, mocker):
        """Test successful non-query execution"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 5
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        result = sql.execute_non_query("INSERT INTO test VALUES (1, 2)")

        assert result == 5
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_non_query_with_params(self, mocker):
        """Test non-query execution with parameters"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 3
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        result = sql.execute_non_query(
            "INSERT INTO {table} VALUES (?, ?)", {"table": "test_table"}
        )

        assert result == 3
        mock_cursor.execute.assert_called_once_with("INSERT INTO test_table VALUES (?, ?)")

    def test_execute_non_query_empty_sql(self, mocker):
        """Test non-query with empty SQL"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.execute_non_query("")

    def test_execute_non_query_error(self, mocker):
        """Test non-query execution error"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        with pytest.raises(SQLExecutionError):
            sql.execute_non_query("INSERT INTO test VALUES (1, 2)")

        mock_conn.rollback.assert_called_once()

    def test_execute_non_query_from_file_success(self, mocker):
        """Test successful non-query from file"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 2
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql_content = "INSERT INTO {table} VALUES (1, 2)"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
            f.write(sql_content)
            temp_path = f.name

        try:
            sql = SQLServer("server", "user", "database")
            result = sql.execute_non_query_from_file(temp_path, {"table": "test_table"})

            assert result == 2
            mock_cursor.execute.assert_called_once_with("INSERT INTO test_table VALUES (1, 2)")
        finally:
            Path(temp_path).unlink()

    def test_bulk_insert_success(self, mocker):
        """Test successful bulk insert"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        mock_to_sql = mocker.patch.object(df, "to_sql")

        sql = SQLServer("server", "user", "database")
        sql.bulk_insert(df, "test_table", batch_size=2)

        mock_to_sql.assert_called_once_with(
            name="test_table",
            con=mock_conn,
            schema="dbo",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=2,
        )

    def test_bulk_insert_invalid_params(self, mocker):
        """Test bulk insert with invalid parameters"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        # Test empty DataFrame
        empty_df = pd.DataFrame()
        with pytest.raises(InvalidParametersError):
            sql.bulk_insert(empty_df, "test_table")

        # Test invalid batch size
        df = pd.DataFrame({"col1": [1, 2]})
        with pytest.raises(InvalidParametersError):
            sql.bulk_insert(df, "test_table", batch_size=0)

    def test_create_table_from_dataframe_success(self, mocker):
        """Test successful table creation from DataFrame"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_to_sql = mocker.patch("pandas.DataFrame.to_sql")

        sql = SQLServer("server", "user", "database")
        sql.create_table_from_dataframe(df, "test_table")

        mock_to_sql.assert_called_once()
        call_args = mock_to_sql.call_args
        assert call_args[1]["name"] == "test_table"
        assert call_args[1]["if_exists"] == "fail"
        assert call_args[1]["index"] is False

    def test_table_exists_true(self, mocker):
        """Test table exists check returning True"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("test_table")

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_table_exists_false(self, mocker):
        """Test table exists check returning False"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = [0]
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("nonexistent_table")

        assert result is False

    def test_table_exists_empty_name(self, mocker):
        """Test table exists with empty table name"""
        mock_conn = mocker.Mock()
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.table_exists("")

    def test_table_exists_no_result(self, mocker):
        """Test table exists when query returns no result"""
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch("nhs_herbot.sql.pyodbc.connect", return_value=mock_conn)

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("test_table")

        assert result is False
