"""
Tests for the nhs_herbot/errors.py module.
"""

import re
import warnings

import pytest

from nhs_herbot import (
    ColumnsNotFoundError,
    DataTypeNotFoundWarning,
    ExceptionRaisedIncorrectlyError,
    InvalidMonthError,
    LoggedException,
    LoggedWarning,
    MergeColumnsNotFoundError,
    MergeWarning,
    NoDataProvidedError,
    NoDatasetsProvidedError,
    NoFilePathProvidedError,
)


class TestCustomExceptions:
    """
    Tests for the custom exception classes including:
    - LoggedException
    - NoFilePathProvidedError
    - NoDatasetsProvidedError
    - NoDataProvidedError
    - ExceptionRaisedIncorrectlyError
    - ColumnsNotFoundError
    - MergeColumnsNotFoundError
    - InvalidMonthError
    """

    @pytest.mark.parametrize(
        "exception_class, message",
        [
            (LoggedException, "Test error message"),
            (NoFilePathProvidedError, "No file path provided"),
            (NoDatasetsProvidedError, "No datasets provided"),
            (NoDataProvidedError, "No data provided"),
            (ExceptionRaisedIncorrectlyError, "Exception raised incorrectly"),
            (InvalidMonthError, "Invalid month provided"),
        ],
    )
    def test_error(self, mock_error, exception_class, message):
        """
        Test that the LoggedException logs the error message.
        """
        with pytest.raises(exception_class, match=message):
            raise exception_class(message)
        mock_error.assert_called_with(message)

    @pytest.mark.parametrize(
        "kwargs_dicts, expected_message",
        [
            (
                {"column_set1": ["test1", "test2"]},
                "Test base message. MISSING COLUMNS: COLUMN_SET1: ['test1', 'test2']",
            ),
            (
                {"column_set1": ["test1", "test2"], "column_set2": ["test3", "test4"]},
                "Test base message. MISSING COLUMNS: COLUMN_SET1: ['test1', 'test2'] COLUMN_SET2: ['test3', 'test4']",
            ),
            (
                {"column_set1": ["test1", "test2", "columnA"]},
                "Test base message. MISSING COLUMNS: COLUMN_SET1: ['test1', 'test2']",
            ),
            (
                {
                    "column_set1": ["test1", "test2"],
                    "column_set2": ["columnA", "columnB"],
                },
                "Test base message. MISSING COLUMNS: COLUMN_SET1: ['test1', 'test2']",
            ),
            (
                {"column_set1": "test1"},
                "Test base message. MISSING COLUMNS: COLUMN_SET1: ['test1']",
            ),
        ],
    )
    def test_columns_not_found_error(self, mock_error, kwargs_dicts, expected_message):
        """
        Test that the ColumnsNotFoundError raises the correct message. Cases include:
        - One column set with all values not found in the dataset_columns
        - Multiple column sets with all values not found in the dataset_columns
        - One column set with some values (not all) not found in the dataset_columns
        - Multiple column sets with some set with all values found in the dataset_columns and some
        sets with all values not found in the dataset_columns
        """
        with pytest.raises(ColumnsNotFoundError, match=re.escape(expected_message)):
            raise ColumnsNotFoundError(
                base_message="Test base message.",
                dataset_columns=[
                    "columnA",
                    "columnB",
                ],
                **kwargs_dicts,
            )
        mock_error.assert_called_with(expected_message)

    @pytest.mark.parametrize(
        "kwargs_dicts",
        [
            {"column_set1": ["columnA", "columnB"]},
            {
                "column_set1": ["columnA", "columnB"],
                "column_set2": ["columnA", "columnB"],
            },
            {"column_set1": ["columnA"], "column_set2": ["columnB"]},
        ],
    )
    def test_columns_not_found_error_bad_raise(self, mock_error, kwargs_dicts):
        """
        Tests that the ColumnsNotFoundError itself raises the ExceptionRaisedIncorrectlyError when
        there are no missing columns. Cases include:
        - One column set with all of the values found in the dataset_columns
        - Multiple column sets with all of the values found in the dataset_columns
        - Multiple column sets with some values found in the dataset_columns.

        Note: These tests are to ensure that the ColumnsNotFoundError is raising correctly when
        there are no missing columns.
        """
        # We only check for the ExceptionRaisedIncorrectlyError here as we haven't found a way for
        # pytest to check for the ColumnsNotFoundError being raised correctly when it is raising
        # the ExceptionRaisedIncorrectlyError.
        with pytest.raises(
            ExceptionRaisedIncorrectlyError,
            match=re.escape("ColumnsNotFoundError was potentially raised incorrectly."),
        ):
            raise ColumnsNotFoundError(
                base_message="When loading the dataset",
                dataset_columns=[
                    "columnA",
                    "columnB",
                ],
                **kwargs_dicts,
            )

        # Instead we rely on the logger mock to check that ColumnsNotFoundError was raised with the
        # correct message as it is a child of the LoggedException error class.
        assert mock_error.call_count == 2
        assert (
            mock_error.call_args_list[0].args[0]
            == "No missing columns found. This error might have raised in error."
        )
        assert (
            mock_error.call_args_list[1].args[0]
            == "ColumnsNotFoundError was potentially raised incorrectly."
        )

    @pytest.mark.parametrize(
        "left_columns, right_columns, left_on, right_on, expected_message",
        [
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                ["col4"],
                "The column(s) ['col4'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                ["col4", "col5"],
                "The column(s) ['col4', 'col5'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                "col4",
                "The column(s) ['col4'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col4"],
                ["col1"],
                "The column(s) ['col4'] were not found in the left dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                "col4",
                ["col1"],
                "The column(s) ['col4'] were not found in the left dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col4"],
                ["col4"],
                "The column(s) ['col4'] were not found in the left dataset. The column(s) ['col4'] were not found in the right dataset.",
            ),
        ],
    )
    def test_merge_columns_not_found_error(
        self,
        mock_error,
        left_columns,
        right_columns,
        left_on,
        right_on,
        expected_message,
    ):
        """
        Test that the MergeColumnsNotFoundError raises the correct message. Cases include:
        - One column in a list not found in the right columns
        - Two columns in a list not found in  the right columns
        - One column as a string not found in the right columns
        - One column in a list not found in the left columns
        - One column as a string not found in the left columns
        - One column in a list not found in the left columns and one column in a list not found in the right columns
        """
        with pytest.raises(MergeColumnsNotFoundError, match=re.escape(expected_message)):
            raise MergeColumnsNotFoundError(left_columns, right_columns, left_on, right_on)
        mock_error.assert_called_with(expected_message)


class TestCustomWarnings:
    """
    Tests for the custom warning classes including:
    - LoggedWarning
    - MergeWarning
    """

    @pytest.mark.parametrize(
        "warning_class, message",
        [
            (LoggedWarning, "Test warning message"),
            (MergeWarning, "Merge warning message"),
            (DataTypeNotFoundWarning, "Data type not found warning message"),
        ],
    )
    def test_warning(self, mock_warning, warning_class, message):
        """
        Test that the LoggedWarning logs the warning message.
        """
        with pytest.warns(warning_class, match=message):
            warnings.warn(message, warning_class)
        mock_warning.assert_called_with(message)


if __name__ == "__main__":
    pytest.main([__file__])
