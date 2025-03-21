"""
Tests for nhs_herbot/utils.py
"""

from datetime import datetime
import re
import time

import pandas as pd
import pytest

from nhs_herbot import utils
from nhs_herbot.errors import ColumnsNotFoundError, DataTypeNotFoundWarning, InvalidMonthError


class TestNormaliseColumnNames:
    """
    Tests for the utils.normalise_column_names function
    """

    @pytest.fixture()
    def input_df(self) -> pd.DataFrame:
        """
        Returns a dataframe with messy column names
        """
        data = {
            " Column A ": [1, 2],
            "Column-B": [3, 4],
            "Column(C)": [5, 6],
            "Column/D": [7, 8],
            "Column.E": [9, 10],
            "Column F": [11, 12],
        }
        df = pd.DataFrame(data)
        return df

    @pytest.mark.parametrize(
        "expected_columns, to_lower, strip, replace_values",
        [
            (
                ["column_a", "columnb", "columnc", "column_d", "column_e", "column_f"],
                True,
                True,
                None,
            ),
            (
                ["Column_A", "ColumnB", "ColumnC", "Column_D", "Column_E", "Column_F"],
                False,
                True,
                None,
            ),
            (
                ["_column_a_", "columnb", "columnc", "column_d", "column_e", "column_f"],
                True,
                False,
                None,
            ),
            (
                ["column a", "column-b", "column(c)", "column/d", "column.e", "column f"],
                True,
                True,
                {" ": " "},
            ),
        ],
    )
    def test_normalise_column_names(
        self, input_df, expected_columns, to_lower, strip, replace_values
    ):
        """
        Test the normalise_column_names function. Cases to test:
            1. Check that the column names are normalised under default conditions
            2. Check that the column names are not cast to lower case
            3. Check that the column names are not stripped
            4. Check that the column names are normalised with a custom replace_values dictionary
        """
        result_df = utils.normalise_column_names(
            df=input_df, to_lower=to_lower, strip=strip, replace_values=replace_values
        )
        assert list(result_df.columns) == expected_columns


class TestUnNormaliseColumnNames:
    """
    Tests for the utils.un_normalise_column_names function
    """

    @pytest.mark.parametrize(
        "input_columns, expected_columns",
        [
            (["column_a"], ["Column A"]),
            (["Column B"], ["Column B"]),
            ([""], [""]),
            (["column_c", "column_d"], ["Column C", "Column D"]),
            (["column__e"], ["Column  E"]),
        ],
    )
    def test_un_normalise_column_names(self, input_columns, expected_columns):
        """
        Tests the un_normalise_column_names function. Cases to test:
            1. Single column name
            2. Already un-normalised column name
            3. Empty column name
            4. Multiple column names
            5. Column name with multiple underscores
        """
        input_df = pd.DataFrame(columns=input_columns)
        result_df = utils.un_normalise_column_names(input_df)
        assert list(result_df.columns) == expected_columns


class TestConvertValuesTo:
    """
    Tests for the utils.convert_values_to function
    """

    @pytest.mark.parametrize(
        "value, match, to, invert_match, expected",
        [
            ("DEV34", None, "DEV02", False, "DEV02"),
            ("DEV35", None, "DEV02", False, "DEV02"),
            ("DEV36", None, "DEV02", False, "DEV36"),
            ("DEV36", ["DEV34", "DEV35"], "DEV02", False, "DEV36"),
            ("DEV34", ["DEV34", "DEV35"], "DEV02", False, "DEV02"),
            ("DEV36", ["DEV34", "DEV35"], "DEV02", True, "DEV02"),
            ("DEV34", ["DEV34", "DEV35"], "DEV02", True, "DEV34"),
        ],
    )
    def test_convert_values_to(self, value, match, to, invert_match, expected):
        """
        Test the convert_values_to function. Cases to test:
            1. Default match list and conversion
            2. Custom match list and conversion
            3. Inverted match logic
        """
        result = utils.convert_values_to(
            value=value, match=match, to=to, invert_match=invert_match
        )
        assert result == expected

    @pytest.mark.parametrize(
        "value, match, to, invert_match, expected",
        [
            (123, None, 456, False, 123),
            (789, [123, 456], 101, False, 789),
            (123, [123, 456], 101, False, 101),
            ([1, 2, 3], None, [4, 5, 6], False, [1, 2, 3]),
            ([1, 2, 3], [[1, 2, 3], [4, 5, 6]], [7, 8, 9], False, [7, 8, 9]),
            ((1, 2), None, (3, 4), False, (1, 2)),
            ((1, 2), [(1, 2), (3, 4)], (5, 6), False, (5, 6)),
        ],
    )
    def test_convert_other_values_to(self, value, match, to, invert_match, expected):
        """
        Test the convert_values_to function with other data types. Cases to test:
            1. Integer conversion
            2. List conversion
            3. Tuple conversion
        """
        result = utils.convert_values_to(
            value=value, match=match, to=to, invert_match=invert_match
        )
        assert result == expected


class TestConvertFinDates:
    """
    Tests for the utils.convert_fin_dates function
    """

    @pytest.mark.parametrize(
        "fin_month, fin_year, expected",
        [
            (1, 202425, pd.Timestamp("2024-04-01")),
            (2, 202425, pd.Timestamp("2024-05-01")),
            (3, 202425, pd.Timestamp("2024-06-01")),
            (4, 202425, pd.Timestamp("2024-07-01")),
            (5, 202425, pd.Timestamp("2024-08-01")),
            (6, 202425, pd.Timestamp("2024-09-01")),
            (7, 202425, pd.Timestamp("2024-10-01")),
            (8, 202425, pd.Timestamp("2024-11-01")),
            (9, 202425, pd.Timestamp("2024-12-01")),
            (10, 202425, pd.Timestamp("2025-01-01")),
            (11, 202425, pd.Timestamp("2025-02-01")),
            (12, 202425, pd.Timestamp("2025-03-01")),
        ],
    )
    def test_convert_fin_dates(self, fin_month, fin_year, expected):
        """
        Test the convert_fin_dates function. Tests all months in a financial year.
        """
        result = utils.convert_fin_dates(fin_month=fin_month, fin_year=fin_year)
        assert result == expected

    @pytest.mark.parametrize(
        "fin_month, fin_year",
        [
            (0, 202425),
            (13, 202425),
            (-1, 202425),
            (14, 202425),
        ],
    )
    def test_convert_fin_dates_invalid_month(self, mock_error, fin_month, fin_year):
        """
        Test the convert_fin_dates function with invalid months. Should raise a ValueError.
        """
        expected_message = "Invalid month. Month should be between 1 and 12."
        with pytest.raises(InvalidMonthError, match=re.escape(expected_message)):
            utils.convert_fin_dates(fin_month=fin_month, fin_year=fin_year)
        mock_error.assert_called_with(expected_message)


class TestConvertFinDatesVectorised:
    """
    Tests for the utils.convert_fin_dates_vectorised function
    """

    @pytest.mark.parametrize(
        "fin_month, fin_year, expected",
        [
            (1, 202425, pd.to_datetime(pd.Series("2024-04-01"))),
            (2, 202425, pd.to_datetime(pd.Series("2024-05-01"))),
            (3, 202425, pd.to_datetime(pd.Series("2024-06-01"))),
            (4, 202425, pd.to_datetime(pd.Series("2024-07-01"))),
            (5, 202425, pd.to_datetime(pd.Series("2024-08-01"))),
            (6, 202425, pd.to_datetime(pd.Series("2024-09-01"))),
            (7, 202425, pd.to_datetime(pd.Series("2024-10-01"))),
            (8, 202425, pd.to_datetime(pd.Series("2024-11-01"))),
            (9, 202425, pd.to_datetime(pd.Series("2024-12-01"))),
            (10, 202425, pd.to_datetime(pd.Series("2025-01-01"))),
            (11, 202425, pd.to_datetime(pd.Series("2025-02-01"))),
            (12, 202425, pd.to_datetime(pd.Series("2025-03-01"))),
        ],
    )
    def test_all_months(self, fin_month, fin_year, expected):
        """
        Tests all months in a financial year.
        """
        input_df = pd.DataFrame({"fin_month": [fin_month], "fin_year": [fin_year]})
        actual = utils.convert_fin_dates_vectorised(input_df, "fin_month", "fin_year")

        pd.testing.assert_series_equal(actual, expected)

    @pytest.mark.parametrize(
        "fin_month, fin_year",
        [
            (0, 202425),
            (13, 202425),
            (-1, 202425),
            (14, 202425),
        ],
    )
    def test_invalid_month(self, mock_error, fin_month, fin_year):
        """
        Tests that the function raises an InvalidMonthError when the month is invalid.
        """
        expected_message = "Invalid month. Month should be between 1 and 12."

        input_df = pd.DataFrame({"fin_month": [fin_month], "fin_year": [fin_year]})

        with pytest.raises(InvalidMonthError, match=re.escape(expected_message)):
            utils.convert_fin_dates_vectorised(input_df, "fin_month", "fin_year")

        mock_error.assert_called_with(expected_message)


class TestParseDates:
    """
    Tests for the utils.parse_dates function
    """

    @pytest.mark.parametrize(
        "date_str, expected",
        [
            ("01/01/2020 12:30", pd.Timestamp("2020-01-01 12:30")),
            ("31/12/2020 23:59", pd.Timestamp("2020-12-31 23:59")),
            ("01/01/2020", pd.Timestamp("2020-01-01")),
            ("31/12/2020", pd.Timestamp("2020-12-31")),
            ("43831", datetime(2020, 1, 1)),  # Excel serial date for 2020-01-01
            ("43830", datetime(2019, 12, 31)),  # Excel serial date for 2019-12-31
            (
                "43830.520833333336",
                datetime(2019, 12, 31, 12, 30),
            ),  # Excel serial date for 2020-01-01 12:30
            (
                "43830.99930555555",
                datetime(2019, 12, 31, 23, 59),
            ),  # Excel serial date for 2019-12-31 23:59
        ],
    )
    def test_parse_dates_valid(self, date_str, expected):
        """
        Test the parse_dates function with valid date strings.
        """
        result = utils.parse_dates(date_str)
        assert result == expected

    @pytest.mark.parametrize(
        "date_str",
        [
            "invalid date",
            "32/01/2020",
            "01/13/2020",
            "01-01-2020",
            "2020/01/01",
        ],
    )
    def test_parse_dates_invalid(self, date_str):
        """
        Test the parse_dates function with invalid date strings. Should return pd.NaT.
        """
        result = utils.parse_dates(date_str)
        assert pd.isna(result)


class TestConvertDatetimeColumnHeaders:
    """
    Tests for the utils.convert_datetime_column_headers function
    """

    @pytest.mark.parametrize(
        "output_format, expected",
        [
            ("%b %Y", ["Jan 2020", "Feb 2020", "Mar 2020"]),
            ("%B %Y", ["January 2020", "February 2020", "March 2020"]),
            ("%m/%Y", ["01/2020", "02/2020", "03/2020"]),
            ("%Y-%m", ["2020-01", "2020-02", "2020-03"]),
        ],
    )
    def test_only_datetime_column_headers(self, output_format, expected):
        """
        Test the convert_datetime_column_headers function with different output formats.
        """
        input_df = pd.DataFrame(
            columns=[
                pd.Timestamp("2020-01-01"),
                pd.Timestamp("2020-02-01"),
                pd.Timestamp("2020-03-01"),
            ]
        )
        result_df = utils.convert_datetime_column_headers(input_df, output_format)
        assert list(result_df.columns) == expected

    def test_mixed_column_headers(self):
        """
        Test the convert_datetime_column_headers function with a mix of datetime and non-datetime column headers.
        """
        input_df = pd.DataFrame(
            columns=[
                pd.Timestamp("2020-01-01"),
                "non_datetime_col",
                pd.Timestamp("2020-02-01"),
                "another_non_datetime_col",
            ]
        )
        result_df = utils.convert_datetime_column_headers(input_df)
        assert list(result_df.columns) == [
            "Jan 2020",
            "non_datetime_col",
            "Feb 2020",
            "another_non_datetime_col",
        ]

    def test_no_datetime_column_headers_warning(self, mock_warning):
        """
        Test the convert_datetime_column_headers function with no datetime column headers. Should log a warning.
        """
        input_df = pd.DataFrame(columns=["col1", "col2", "col3"])
        expected_message = "No datetime columns found in the DataFrame."

        with pytest.warns(DataTypeNotFoundWarning, match=re.escape(expected_message)):
            utils.convert_datetime_column_headers(input_df)
        mock_warning.assert_called_with(expected_message)


class TestSortStringListWithDates:
    """
    Tests for the utils.sort_string_list_with_dates function
    """

    def test_empty_string_list(self):
        """
        Test the sort_string_list_with_dates function with an empty string list.
        """
        result = utils.sort_string_list_with_dates([])
        assert not result

    def test_returns_list_of_strings(self):
        """
        Test the sort_string_list_with_dates function returns a list of strings.
        """
        result = utils.sort_string_list_with_dates(["Jan 2020", "Feb 2020", "Mar 2020"])
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    @pytest.mark.parametrize(
        "list_of_strings, format, expected",
        [
            (["test1", "test3", "test2"], "%b %Y", ["test1", "test2", "test3"]),
            (
                ["Mar 2020", "Jan 2020", "Feb 2020"],
                "%b %Y",
                ["Jan 2020", "Feb 2020", "Mar 2020"],
            ),
            (
                ["2020-03", "2020-01", "2020-02"],
                "%Y-%m",
                ["2020-01", "2020-02", "2020-03"],
            ),
            (
                ["2020-01", "not_date", "2020-02"],
                "%Y-%m",
                ["not_date", "2020-01", "2020-02"],
            ),
            (
                ["2020-01", "Jan 2020", "2020-02"],
                "%Y-%m",
                ["Jan 2020", "2020-01", "2020-02"],
            ),
        ],
    )
    def test_sort_string_list_with_dates(self, list_of_strings, format, expected):
        """
        Test the sort_string_list_with_dates function with different date formats.
        """
        result = utils.sort_string_list_with_dates(list_of_strings, format)
        assert result == expected


class TestCalcChangeFromPreviousMonthColumn:
    """
    Tests for the utils.calc_change_from_previous_month_column function
    """

    @pytest.fixture()
    def monthly_summary_table(self) -> pd.DataFrame:
        """
        Returns a dataframe with datetime columns and some data
        """
        data = {
            pd.Timestamp("2023-01-01"): [100, 200, 300],
            pd.Timestamp("2023-02-01"): [110, 210, 310],
            pd.Timestamp("2023-03-01"): [120, 220, 320],
        }
        df = pd.DataFrame(data)
        return df

    def test_default_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with default columns
        """
        result_df = utils.calc_change_from_previous_month_column(monthly_summary_table)
        expected_change = [10, 10, 10]
        assert list(result_df["change_from_previous_month"]) == expected_change

    def test_specified_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with specified columns
        """
        result_df = utils.calc_change_from_previous_month_column(
            monthly_summary_table,
            most_recent_col=pd.Timestamp("2023-02-01"),
            second_most_recent_col=pd.Timestamp("2023-01-01"),
        )
        expected_change = [10, 10, 10]
        assert list(result_df["change_from_previous_month"]) == expected_change

    def test_missing_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with missing columns
        """
        match = re.escape(
            "Columns were not found in the dataset. MISSING COLUMNS: MOST_RECENT_COL: "
            "['non_existent_col']"
        )
        with pytest.raises(ColumnsNotFoundError, match=match):
            utils.calc_change_from_previous_month_column(
                monthly_summary_table,
                most_recent_col="non_existent_col",
                second_most_recent_col=pd.Timestamp("2023-01-01"),
            )

    def test_with_nan_values(self):
        """
        Test the calc_change_from_previous_month_column function with NaN values
        """
        data = {
            pd.Timestamp("2023-01-01"): [100, None, 300],
            pd.Timestamp("2023-02-01"): [110, 210, None],
        }
        df = pd.DataFrame(data)
        result_df = utils.calc_change_from_previous_month_column(df)
        expected_change = [10, 210, -300]
        assert list(result_df["change_from_previous_month"]) == expected_change


class TestReplaceListElementWithList:
    """
    Tests for the utils.replace_list_element_with_list function
    """

    @pytest.mark.parametrize(
        "main_list, insert_list, match_value, expected",
        [
            ([1, 2, 3], [4, 5], 2, [1, 4, 5, 3]),
            (["a", "b", "c"], ["x", "y"], "b", ["a", "x", "y", "c"]),
            ([1, 2, 3], [4, 5], 1, [4, 5, 2, 3]),
            ([1, 2, 3], [4, 5], 3, [1, 2, 4, 5]),
            ([1, 2, 3], [], 2, [1, 3]),
        ],
    )
    def test_replace_list_element_with_list(self, main_list, insert_list, match_value, expected):
        """
        Test the replace_list_element_with_list function. Cases to test:
            1. Replace an element in the middle of the list
            2. Replace an element in the middle of the list with strings
            3. Replace the first element in the list
            4. Replace the last element in the list
            5. Replace an element with an empty list
        """
        result = utils.replace_list_element_with_list(main_list, insert_list, match_value)
        assert result == expected

    def test_replace_list_element_with_list_no_match(self):
        """
        Test the replace_list_element_with_list function when the match_value is not in the list.
        Should raise a ValueError.
        """
        main_list = [1, 2, 3]
        insert_list = [4, 5]
        match_value = 6
        with pytest.raises(ValueError):
            utils.replace_list_element_with_list(main_list, insert_list, match_value)


class TestTimeit:
    """
    Tests for the utils.timeit decorator
    """

    @pytest.fixture
    def mock_logger(self, mocker):
        """
        Fixture to mock the logger
        """
        return mocker.patch("nhs_herbot.utils.logger")

    def test_timeit_decorator(self, mock_logger):
        """
        Test the timeit decorator to ensure it logs the execution time
        """

        @utils.timeit
        def sample_function():
            time.sleep(0.1)
            return "result"

        result = sample_function()
        assert result == "result"
        assert mock_logger.debug.called
        log_message = mock_logger.debug.call_args[0][0]
        assert re.match(r"Function 'sample_function' executed in \d+\.\d+ s", log_message)

    def test_timeit_decorator_with_args(self, mock_logger):
        """
        Test the timeit decorator with a function that takes arguments
        """

        @utils.timeit
        def sample_function(x, y):
            time.sleep(0.1)
            return x + y

        result = sample_function(1, 2)
        assert result == 3
        assert mock_logger.debug.called
        log_message = mock_logger.debug.call_args[0][0]
        assert re.match(r"Function 'sample_function' executed in \d+\.\d+ s", log_message)

    def test_timeit_decorator_with_kwargs(self, mock_logger):
        """
        Test the timeit decorator with a function that takes keyword arguments
        """

        @utils.timeit
        def sample_function(x, y=0):
            time.sleep(0.1)
            return x + y

        result = sample_function(1, y=2)
        assert result == 3
        assert mock_logger.debug.called
        log_message = mock_logger.debug.call_args[0][0]
        assert re.match(r"Function 'sample_function' executed in \d+\.\d+ s", log_message)


class TestSortByPriority:
    """
    Tests for the utils.sort_by_priority function
    """

    @pytest.fixture()
    def input_df(self) -> pd.DataFrame:
        """
        Returns a dataframe with a column to be sorted by priority
        """
        data = {
            "priority_column": ["low", "high", "medium", "low", "high"],
            "values": [1, 2, 3, 4, 5],
        }
        df = pd.DataFrame(data)
        return df

    @pytest.mark.parametrize(
        "priorities, expected_order",
        [
            (["high", "medium", "low"], ["high", "high", "medium", "low", "low"]),
            (["low", "medium", "high"], ["low", "low", "medium", "high", "high"]),
            (["medium", "low", "high"], ["medium", "low", "low", "high", "high"]),
            ([], ["low", "high", "medium", "low", "high"]),
        ],
    )
    def test_sort_by_priority(self, input_df, priorities, expected_order):
        """
        Test the sort_by_priority function with different priority orders
        """
        result_df = utils.sort_by_priority(input_df, "priority_column", priorities)
        assert list(result_df["priority_column"]) == expected_order

    def test_sort_by_priority_with_missing_values(self):
        """
        Test the sort_by_priority function with values not in the priority list
        """
        data = {
            "priority_column": ["low", "high", "medium", "unknown", "high"],
            "values": [1, 2, 3, 4, 5],
        }
        df = pd.DataFrame(data)
        priorities = ["high", "medium", "low"]
        expected_order = ["high", "high", "medium", "low", "unknown"]
        result_df = utils.sort_by_priority(df, "priority_column", priorities)
        assert list(result_df["priority_column"]) == expected_order

    def test_sort_by_priority_with_empty_dataframe(self):
        """
        Test the sort_by_priority function with an empty dataframe
        """
        df = pd.DataFrame(columns=["priority_column", "values"])
        priorities = ["high", "medium", "low"]
        result_df = utils.sort_by_priority(df, "priority_column", priorities)
        assert result_df.empty

    def test_sort_by_priority_with_no_priority_column(self):
        """
        Test the sort_by_priority function when the priority column does not exist
        """
        df = pd.DataFrame({"values": [1, 2, 3, 4, 5]})
        priorities = ["high", "medium", "low"]
        with pytest.raises(KeyError):
            utils.sort_by_priority(df, "priority_column", priorities)


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
