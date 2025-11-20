"""
Tests for nhs_herbot/sql.py SQLServer class
"""

import pandas as pd
import pytest

from nhs_herbot.errors import (
    DatabaseConnectionError,
    InvalidParametersError,
    SQLExecutionError,
)
from nhs_herbot.sql import SQLServer


class TestSQLServer:
    """Tests for SQLServer class"""

    def test_init_success(self, mock_pyodbc):
        """Test successful initialization"""
        sql = SQLServer("server", "user", "database")

        assert sql.server == "server"
        assert sql.uid == "user"
        assert sql.database == "database"
        assert sql.driver == "ODBC Driver 17 for SQL Server"
        assert sql.timeout == 30
        mock_pyodbc.connect.assert_called_once()

    def test_init_custom_driver(self, mock_pyodbc):
        """Test initialization with custom driver"""
        sql = SQLServer("server", "user", "database", driver="ODBC Driver 18 for SQL Server")

        assert sql.driver == "ODBC Driver 18 for SQL Server"

    def test_init_invalid_parameters(self, mock_pyodbc):
        """Test initialization with invalid parameters"""
        with pytest.raises(InvalidParametersError):
            SQLServer("", "user", "database")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "", "database")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "user", "")

        with pytest.raises(InvalidParametersError):
            SQLServer("server", "user", "database", timeout=-1)

    def test_init_connection_failure(self, mock_pyodbc):
        """Test connection failure during initialization"""
        mock_pyodbc.connect.side_effect = Exception("Connection failed")

        with pytest.raises(DatabaseConnectionError):
            SQLServer("server", "user", "database")

    def test_query_success(self, mock_pyodbc, mocker):
        """Test successful query execution"""
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("nhs_herbot.sql.pd.read_sql", return_value=mock_df)

        sql = SQLServer("server", "user", "database")
        result = sql.query("SELECT * FROM test")

        assert result.equals(mock_df)

    def test_query_empty_sql(self, mock_pyodbc):
        """Test query with empty SQL"""
        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.query("")

    def test_query_execution_error(self, mock_pyodbc, mocker):
        """Test query execution error"""
        mocker.patch("nhs_herbot.sql.pd.read_sql", side_effect=Exception("SQL error"))

        sql = SQLServer("server", "user", "database")

        with pytest.raises(SQLExecutionError):
            sql.query("SELECT * FROM test")

    def test_query_from_file_success(self, mock_pyodbc, mocker, tmp_path):
        """Test successful query from file"""
        mock_df = pd.DataFrame({"col1": [1, 2]})
        mocker.patch("nhs_herbot.sql.pd.read_sql", return_value=mock_df)

        sql_content = "SELECT * FROM {table_name}"

        # Create a temporary SQL file using pytest's tmp_path fixture
        temp_file = tmp_path / "test_query.sql"
        temp_file.write_text(sql_content)

        sql = SQLServer("server", "user", "database")
        result = sql.query_from_file(str(temp_file), {"table_name": "test_table"})

        assert result.equals(mock_df)

    def test_query_from_file_not_found(self, mock_pyodbc):
        """Test query from non-existent file"""
        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError) as exc_info:
            sql.query_from_file("/nonexistent/file.sql")

        assert "SQL file not found" in str(exc_info.value)

    def test_close_connection(self, mock_pyodbc):
        """Test closing connection"""
        sql = SQLServer("server", "user", "database")
        sql.close()

        mock_pyodbc.connect.return_value.close.assert_called_once()

    def test_context_manager(self, mock_pyodbc):
        """Test context manager usage"""
        with SQLServer("server", "user", "database") as sql:
            assert isinstance(sql, SQLServer)

        mock_pyodbc.connect.return_value.close.assert_called_once()

    def test_write_dataframe_success(self, mock_pyodbc, mocker):
        """Test successful DataFrame write"""
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_to_sql = mocker.patch.object(df, "to_sql")

        sql = SQLServer("server", "user", "database")
        sql.write_dataframe(df, "test_table")

        mock_to_sql.assert_called_once_with(
            name="test_table",
            con=mock_pyodbc.connect.return_value,
            schema="dbo",
            if_exists="fail",
            index=False,
            method=None,
            chunksize=None,
        )

    def test_write_dataframe_invalid_params(self, mock_pyodbc):
        """Test write DataFrame with invalid parameters"""
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

    def test_execute_non_query_success(self, mock_pyodbc, mocker):
        """Test successful non-query execution"""
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 5
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")
        result = sql.execute_non_query("INSERT INTO test VALUES (1, 2)")

        assert result == 5
        mock_cursor.execute.assert_called_once()
        mock_pyodbc.connect.return_value.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_non_query_with_params(self, mock_pyodbc, mocker):
        """Test non-query execution with parameters"""
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 3
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")
        result = sql.execute_non_query(
            "INSERT INTO {table} VALUES (?, ?)", {"table": "test_table"}
        )

        assert result == 3
        mock_cursor.execute.assert_called_once_with("INSERT INTO test_table VALUES (?, ?)")

    def test_execute_non_query_empty_sql(self, mock_pyodbc):
        """Test non-query with empty SQL"""
        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.execute_non_query("")

    def test_execute_non_query_error(self, mock_pyodbc, mocker):
        """Test non-query execution error"""
        mock_cursor = mocker.Mock()
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")

        with pytest.raises(SQLExecutionError):
            sql.execute_non_query("INSERT INTO test VALUES (1, 2)")

        mock_pyodbc.connect.return_value.rollback.assert_called_once()

    def test_execute_non_query_from_file_success(self, mock_pyodbc, mocker, tmp_path):
        """Test successful non-query from file"""
        mock_cursor = mocker.Mock()
        mock_cursor.rowcount = 2
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql_content = "INSERT INTO {table} VALUES (1, 2)"

        # Create a temporary SQL file using pytest's tmp_path fixture
        temp_file = tmp_path / "test_insert.sql"
        temp_file.write_text(sql_content)

        sql = SQLServer("server", "user", "database")
        result = sql.execute_non_query_from_file(str(temp_file), {"table": "test_table"})

        assert result == 2
        mock_cursor.execute.assert_called_once_with("INSERT INTO test_table VALUES (1, 2)")

    def test_bulk_insert_success(self, mock_pyodbc, mocker):
        """Test successful bulk insert"""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        mock_to_sql = mocker.patch.object(df, "to_sql")

        sql = SQLServer("server", "user", "database")
        sql.bulk_insert(df, "test_table", batch_size=2)

        mock_to_sql.assert_called_once_with(
            name="test_table",
            con=mock_pyodbc.connect.return_value,
            schema="dbo",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=2,
        )

    def test_bulk_insert_invalid_params(self, mock_pyodbc):
        """Test bulk insert with invalid parameters"""
        sql = SQLServer("server", "user", "database")

        # Test empty DataFrame
        empty_df = pd.DataFrame()
        with pytest.raises(InvalidParametersError):
            sql.bulk_insert(empty_df, "test_table")

        # Test invalid batch size
        df = pd.DataFrame({"col1": [1, 2]})
        with pytest.raises(InvalidParametersError):
            sql.bulk_insert(df, "test_table", batch_size=0)

    def test_create_table_from_dataframe_success(self, mock_pyodbc, mocker):
        """Test successful table creation from DataFrame"""
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_to_sql = mocker.patch("pandas.DataFrame.to_sql")

        sql = SQLServer("server", "user", "database")
        sql.create_table_from_dataframe(df, "test_table")

        mock_to_sql.assert_called_once()
        call_args = mock_to_sql.call_args
        assert call_args[1]["name"] == "test_table"
        assert call_args[1]["if_exists"] == "fail"
        assert call_args[1]["index"] is False

    def test_table_exists_true(self, mock_pyodbc, mocker):
        """Test table exists check returning True"""
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = [1]
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("test_table")

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_table_exists_false(self, mock_pyodbc, mocker):
        """Test table exists check returning False"""
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = [0]
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("nonexistent_table")

        assert result is False

    def test_table_exists_empty_name(self, mock_pyodbc):
        """Test table exists with empty table name"""
        sql = SQLServer("server", "user", "database")

        with pytest.raises(InvalidParametersError):
            sql.table_exists("")

    def test_table_exists_no_result(self, mock_pyodbc, mocker):
        """Test table exists when query returns no result"""
        mock_cursor = mocker.Mock()
        mock_cursor.fetchone.return_value = None
        mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor

        sql = SQLServer("server", "user", "database")
        result = sql.table_exists("test_table")

        assert result is False
