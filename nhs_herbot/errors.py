"""
Defines custom exceptions for the nhs_herbot package.
"""

from loguru import logger


class LoggedException(Exception):
    """
    Custom exception class that logs the error message using the logger.
    """

    def __init__(self, message):
        self.message = message.replace("\n", " ").replace("\t", "")

        logger.error(self.message)
        super().__init__(self.message)


class NoFilePathProvidedError(LoggedException):
    """
    Exception raised when no file path is provided to the `load_csv_data` function.
    """


class NoDatasetsProvidedError(LoggedException):
    """
    Exception raised when no datasets are provided to the `load_datasets` function.
    """


class NoDataProvidedError(LoggedException):
    """
    Exception raised when no data is provided to the `batch_normalise_column_names` function.
    """


class ExceptionRaisedIncorrectlyError(LoggedException):
    """
    Exception raised when an exception is potential raised incorrectly.
    """


class ColumnsNotFoundError(LoggedException):
    """
    Exception raised when the columns are not found in the dataset. Works out which columns are
    missing and builds a message to display.

    If no missing columns are found, this error has been raised incorrectly and a new
    `ExceptionRaisedIncorrectlyError` is raised.

    Parameters
    ----------
    dataset_columns : list
        The columns in the dataset. Use the `columns` attribute of the DataFrame.
    base_message : str, optional
        The base message to display, by default "Columns were not found in the dataset."
    **column_sets : dict
        The column sets to check for. The key is the name of the column set and the value is a
        list of columns that should be present in the dataset.

    Raises
    ------
    ExceptionRaisedIncorrectlyError
        If no missing columns are found, this error has been raised incorrectly.

    Example
    -------
    ```python
    dataset = pd.DataFrame(columns=["columnA", "columnB"])
    raise ColumnsNotFoundError(
        base_message="Example Message",
        dataset_columns=dataset.columns,
        base_columns=["column1", "column2"],
        extra_columns=["column3", "column4"],
    )
    ```
    Would raise an exception with the message:
    ```
    Example Message
    MISSING COLUMNS:
        BASE COLUMNS: ['column1', 'column2']
        EXTRA COLUMNS: ['column3', 'column4']
    ```
    """

    def __init__(
        self,
        dataset_columns,
        base_message="Columns were not found in the dataset.",
        **column_sets,
    ):
        missing_columns_message_start = "MISSING COLUMNS:"
        columns_messages = []
        for column_set_name, column_set in column_sets.items():
            if isinstance(column_set, str):
                column_set = [column_set]
            missing_columns = sorted(set(column_set) - set(dataset_columns))
            if missing_columns:
                columns_messages += [f"\t{column_set_name.upper()}: {missing_columns}"]
        if columns_messages:
            self.message = "\n\t".join(
                [base_message, missing_columns_message_start] + columns_messages
            )
            print(repr(self.message))
            super().__init__(self.message)
        else:
            self.message = "No missing columns found. This error might have raised in error."
            super().__init__(self.message)
            raise ExceptionRaisedIncorrectlyError(
                __class__.__name__ + " was potentially raised incorrectly."
            ) from self


class MergeColumnsNotFoundError(LoggedException):
    """
    Exception raised when the columns are not found in the dataset. Works out which columns are
    missing and builds a message to display.

    Parameters
    ----------
    left_columns : list
        The columns in the left dataset.
    right_columns : list
        The columns in the right dataset.
    left_on : list
        The columns to merge on in the left dataset.
    right_on : list
        The columns to merge on in the right dataset.
    """

    def __init__(self, left_columns, right_columns, left_on, right_on):
        if isinstance(left_on, str):
            left_on = [left_on]
        if isinstance(right_on, str):
            right_on = [right_on]
        self.bad_left = sorted(set(left_on) - set(left_columns))
        self.bad_right = sorted(set(right_on) - set(right_columns))
        parts = []
        if self.bad_left:
            parts.append(f"The column(s) {self.bad_left} were not found in the left dataset.")
        if self.bad_right:
            parts.append(f"The column(s) {self.bad_right} were not found in the right dataset.")
        self.message = " ".join(parts)
        super().__init__(self.message)


class InvalidMonthError(LoggedException):
    """
    Exception raised when an invalid month is provided.
    """


class DatabaseConnectionError(LoggedException):
    """
    Exception raised when database connection fails.
    """


class SQLExecutionError(LoggedException):
    """
    Exception raised when SQL query execution fails.
    """


class InvalidSQLParametersError(LoggedException):
    """
    Exception raised when invalid parameters are provided to SQL functions.
    """


class InvalidParametersError(LoggedException):
    """
    Exception raised when invalid parameters are provided to functions.
    """


class PathNotFoundError(LoggedException):
    """
    Exception raised when the path is not found.
    """

    def __init__(self, path):
        self.message = f"Path not found: {path}"
        super().__init__(self.message)


class DataSetNotFoundError(LoggedException):
    """
    Exception raised when a dataset is not found in a dataset dictionary.
    """


class DuplicateDataError(LoggedException):
    """Custom error for when duplicate data are found in a dataset"""


class LoggedWarning(Warning):
    """
    Custom warning class that logs the warning message using the logger.

    Can be used in two ways:
    1. Traditional: warnings.warn("message", LoggedWarning)
    2. Direct call: LoggedWarning().warn("message")

    The direct call method logs the warning without using the warnings module,
    which provides cleaner output.
    """

    def __init__(self, message=None):
        if message is not None:
            self.message = message
            logger.warning(self.message)
            super().__init__(self.message)

    def warn(self, message):
        """
        Log a warning message directly without using warnings.warn.

        Parameters
        ----------
        message : str
            The warning message to log.
        """
        self.message = message
        logger.warning(self.message)


class MergeWarning(LoggedWarning):
    """Custom warning for merge validation"""


class DataTypeNotFoundWarning(LoggedWarning):
    """Custom warning for when a data type is not found in a collection"""


class DuplicateDataWarning(LoggedWarning):
    """Custom warning for when duplicate data are found in a dataset"""
