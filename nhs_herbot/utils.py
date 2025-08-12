"""
This module provides utility functions for data manipulation and transformation,
including functions for normalizing and un-normalizing column names, converting
financial dates, parsing date strings, sorting lists with dates, and more.
"""

from datetime import datetime, timedelta
import time
from typing import Any, Dict, List, Optional, Union
import warnings

from loguru import logger
import numpy as np
import pandas as pd

from nhs_herbot.errors import DataTypeNotFoundWarning, InvalidMonthError


def normalise_column_names(
    df: pd.DataFrame,
    to_lower: bool = True,
    strip: bool = True,
    replace_values: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Normalise the column names of a dataframe. By default:
        * The column names are cast to all lower case
        * Whitespace around the columns are remove
        * Punctuation and spaces are removed or replaced with underscores, "_".

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with messy column names
    to_lower : bool, optional
        Cast column names to lower case, by default True
    strip : bool, optional
        Strip whitespace from start and end of column names, by default True
    replace_values : Optional[Dict[str, str]], optional
        Dictionary of values to be replaces, by default {
        "-": "",
        "  ": " ",
        "(": "",
        ")": "",
        "/": "_",
        ".": "_",
        " ": "_",
    }

    Returns
    -------
    pd.DataFrame
        Dataframe with cleaned column names
    """
    if to_lower:
        df.columns = df.columns.str.lower()

    if strip:
        df.columns = df.columns.str.strip()

    replace_values = (
        {
            "-": "",
            "  ": " ",
            "(": "",
            ")": "",
            "/": "_",
            ".": "_",
            " ": "_",
        }
        if not replace_values
        else replace_values
    )

    for pat, repl in replace_values.items():
        df.columns = df.columns.map(lambda x, pat=pat, repl=repl: x.replace(pat, repl))

    return df


def un_normalise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame, removes any underscores from the column names, and converts them to title
    case, getting them ready for human friendly presentation.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with normalised column names (lower case, underscores)

    Returns
    -------
    pd.DataFrame
        The DataFrame with un-normalised column names (title case, spaces)
    """
    df.columns = df.columns.str.replace("_", " ").str.title()
    return df


def convert_values_to(
    value: Any, match: Union[List[Any], Any], to: Any, invert_match: bool = False
) -> Any:
    """
    If value matches the match list then it is converted to the provided "to" value. If invert_match
    is true then every value not in the match list will be converted and only matches will
    be unchanged.

    Parameters
    ----------
    value : Any
        Value to convert if they are a match
    match : List[Any], optional
        List of values to match the value to
    to : Any, optional
        Value to convert matched values to
    invert_match : bool, optional
        Invert the match, and convert values that do not match the provided match list, defaults to
        False

    Returns
    -------
    Any
        Converted value or current value if not a match
    """
    match = match if isinstance(match, list) else [match]
    if invert_match:
        return to if value not in match else value
    return to if value in match else value


def convert_fin_dates(fin_month: int, fin_year: int) -> pd.Timestamp:
    """
    Convert financial dates to a pandas datetime, assuming the financial year starts in April and
    the year is given in the form of CCYY1YY2 so 2024-2025 will be 202425

    Parameters
    ----------
    fin_month : int
        Financial month, assumes 1 is April and 12 is March
    fin_year : int
        Financial year, in the format CCYY1YY2, e.g. 202425 is equivalent to 2024-2025

    Returns
    -------
    pd.Timestamp
        Corresponding datetime
    """
    if fin_month < 1 or fin_month > 12:
        raise InvalidMonthError("Invalid month. Month should be between 1 and 12.")
    fin_year_str = str(fin_year)
    century = fin_year_str[:2]
    year_1 = fin_year_str[2:4]
    year_2 = fin_year_str[4:]
    if fin_month <= 9:
        year = century + year_1
        month = str(fin_month + 3)
    else:
        year = century + year_2
        month = str(fin_month - 9)

    return pd.to_datetime(f"{month}, {year}")


def convert_fin_dates_vectorised(
    df: pd.DataFrame,
    fin_month_col: str,
    fin_year_col: str,
) -> pd.Series:
    """
    Convert financial dates in a DataFrame to a pandas datetime, assuming the financial year starts
    in April and the year is given in the form of CCYY1YY2 so 2024-2025 will be 202425.

    This is a more efficient vectorised version of the `convert_fin_dates` function that take in a
    whole dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing financial month and year columns
    fin_month_col : str
        Name of the column containing financial months, assumes 1 is April and 12 is March
    fin_year_col : str
        Name of the column containing financial years, in the format CCYY1YY2, e.g. 202425 is
        equivalent to 2024-2025

    Returns
    -------
    pd.Series
        Series of corresponding datetimes
    """
    fin_year_str = df[fin_year_col].astype(str)
    century = fin_year_str.str[:2]
    year_1 = fin_year_str.str[2:4]
    year_2 = fin_year_str.str[4:]

    month = df[fin_month_col]
    if month.min() < 1 or month.max() > 12:
        raise InvalidMonthError("Invalid month. Month should be between 1 and 12.")

    year = pd.Series(np.where(month <= 9, century + year_1, century + year_2))
    month = pd.Series(np.where(month <= 9, month + 3, month - 9))

    return pd.to_datetime(year + "-" + month.astype(int).astype(str) + "-01")


def parse_dates(
    date_str: str,
) -> Union[pd.Timestamp, pd._typing.DatetimeNaTType, datetime]:  # type: ignore
    """
    Parses a date string into a pandas Timestamp, NaT, or datetime object.
    The function attempts to parse the input date string using the following formats:
        1. "%d/%m/%Y %H:%M" - Day/Month/Year Hour:Minute
        2. "%d/%m/%Y" - Day/Month/Year
        3. Excel serial date format - Days since 1899-12-30
    If the input string cannot be parsed using any of these formats, the function returns pandas
    NaT.

    Parameters:
        date_str (str): The date string to be parsed.
    Returns:
        Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType, datetime]: The parsed date as a pandas Timestamp, NaT, or
        datetime object.
    """
    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y %H:%M")
    except ValueError:
        pass

    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y")
    except ValueError:
        pass

    try:
        return datetime(1899, 12, 30) + timedelta(days=float(date_str))
    except ValueError:
        return pd.NaT


def sort_string_list_with_dates(list_of_strings: List[str], format: str = "%b %Y") -> List[str]:
    """
    Sort a list of strings that may contain dates in the format specified by the format parameter.
    The function will attempt to parse the date strings using the specified format and sort the
    list in ascending order based on the parsed dates. If a string cannot be parsed as a date, it
    will be sorted based on the original string.

    Date string will be sorted after the non-date strings.

    Parameters
    ----------
    list_of_strings : List[str]
        The list of strings to be sorted
    format : str, optional
        The format of the date strings, by default "%b %Y", e.g. "Jan 2021"

    Returns
    -------
    List[str]
        The sorted list of strings
    """

    def parse_date(date_string):
        try:
            return datetime.strptime(date_string, format)
        except ValueError:
            return None

    def sort_key(string):
        date = parse_date(string)
        return (date is not None, date or string)

    return sorted(list_of_strings, key=sort_key)


def convert_datetime_column_headers(
    data: pd.DataFrame, output_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Convert datetime column headers to string with a specified format.

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame with some datetime column headers
    output_format : str, optional
        The output format to convert the datetime column headers to using the pandas strftime,
        defaults to "%b %Y" which will yield "Jan 2021" from pd.Timestamp("2021-01-01")
    """
    output_format = output_format or "%b %Y"

    if not any(isinstance(col, pd.Timestamp) for col in data.columns):
        warnings.warn("No datetime columns found in the DataFrame.", DataTypeNotFoundWarning)
    else:
        data.columns = data.columns.map(
            lambda x: x.strftime(output_format) if isinstance(x, pd.Timestamp) else x
        )
    return data


def get_datetime_columns(data: pd.DataFrame) -> List[pd.Timestamp]:
    """
    Get the datetime columns from the data.

    Parameters
    ----------
    data : pd.DataFrame
        The data to get the datetime columns from

    Returns
    -------
    List[Union[str, pd.Timestamp]]
        The datetime columns in the data
    """
    return [col for col in data.columns if isinstance(col, pd.Timestamp)]


def replace_list_element_with_list(
    main_list: List[Any], insert_list: List[Any], match_value: Any
) -> List[Any]:
    """
    Replace an element in a list with another list. The function will replace the first occurrence
    of the match_value in the main_list with the insert_list.

    Parameters
    ----------
    main_list : List[Any]
        The main list to replace the element in
    insert_list : List[Any]
        The list to insert in place of the match_value
    match_value : Any
        The value to match in the main_list

    Returns
    -------
    List[Any]
        The main_list with the match_value replaced with the insert_list
    """
    index = main_list.index(match_value)
    return main_list[:index] + insert_list + main_list[index + 1 :]  # noqa: E203


def timeit(func):
    """
    A decorator that measures the execution time of a function and logs the duration.

    Parameters
    ----------
    func : callable
        The function to be wrapped and timed.

    Returns
    -------
    callable
        The wrapped function with added timing functionality.

    Notes
    -----
    The execution time is logged using the `logger.debug` method.
    """

    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        logger.debug(f"Function '{func.__name__}' executed in {duration:f} s")
        return result

    return wrapped


def sort_by_priority(data: pd.DataFrame, column: str, priorities: List[str]) -> pd.DataFrame:
    """
    Sort a DataFrame by a column based on a list of priorities.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame to be sorted.
    column : str
        The column name to sort by.
    priorities : List[str]
        The list of priorities to sort by.

    Returns
    -------
    pd.DataFrame
        The sorted DataFrame.
    """

    def priority(value: str) -> int:
        try:
            return priorities.index(value)
        except ValueError:
            return len(priorities)

    return data.sort_values(
        column,
        key=lambda col: col.map(priority),
    )


def convert_to_numeric_column(column: pd.Series) -> pd.Series:
    """
    Convert a column to numeric, removing any commas and converting to float,
    coercing any errors

    Parameters
    ----------
    column : pd.Series
        The column to convert to numeric

    Returns
    -------
    pd.Series
        The converted column
    """
    return pd.to_numeric(column.astype(str).str.replace(",", ""), errors="coerce")


def format_numeric_value(
    value: Union[float, int],
    decimals: int = 2,
    thousands: str = ",",
    prefix: str = "",
    suffix: str = "",
) -> str:
    """
    Format a numeric value to a string with the specified number of decimal places,
    thousands separator, and prefix.

    Parameters
    ----------
    value : Union[float, int]
        The numeric value to format
    decimals : int, optional
        The number of decimal places to display, by default 2
    thousands : str, optional
        The thousands separator, by default ","
    prefix : str, optional
        The prefix to add to the formatted string, by default ""
    suffix : str, optional
        The suffix to add to the formatted string, by default ""

    Returns
    -------
    str
        The formatted value as a string
    """
    if isinstance(value, (float, int)) and pd.notnull(value):
        return f"{prefix}{value:,.{decimals}f}{suffix}".replace(",", thousands)
    if pd.isna(value):
        return value
    return value


def format_numeric_column(
    column: pd.Series,
    decimals: int = 2,
    thousands: str = ",",
    prefix: str = "",
    suffix: str = "",
) -> pd.Series:
    """
    Format a numeric column to a string with the specified number of decimal places,
    thousands separator, and prefix.

    Parameters
    ----------
    column : pd.Series
        The column to format
    decimals : int, optional
        The number of decimal places to display, by default 2
    thousands : str, optional
        The thousands separator, by default ","
    prefix : str, optional
        The prefix to add to the formatted string, by default ""
    suffix : str, optional
        The suffix to add to the formatted string, by default ""

    Returns
    -------
    pd.Series
        The formatted column
    """
    return column.apply(
        format_numeric_value,
        decimals=decimals,
        thousands=thousands,
        prefix=prefix,
        suffix=suffix,
    )
