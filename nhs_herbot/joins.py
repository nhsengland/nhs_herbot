"""
Functions for processing the datasets for the pipeline.
"""

from typing import List, Literal, Optional, Union
import warnings

from loguru import logger
import pandas as pd

from nhs_herbot.errors import MergeColumnsNotFoundError, MergeWarning

MergeHow = Literal["left", "right", "outer", "inner"]


def check_merge_health(
    merged_df: pd.DataFrame, merge_column: Optional[str] = "_merge", keep_merge: bool = False
) -> pd.DataFrame:
    """
    Check the merge for any issues and return the merged DataFrame.

    Parameters
    ----------
    merged_df : pd.DataFrame
        The merged DataFrame to check.
    merge_column : str, optional
        The column to check for issues, by default "_merge"

    Returns
    -------
    pd.DataFrame
        The merged DataFrame.
    """
    merge_column = merge_column or "_merge"

    if merge_column not in merged_df.columns:
        logger.info(f"The merge column, {merge_column}, was not found in the merged dataframe")
        return merged_df

    bad_merge_found = False
    for bad_merge in ("left_only", "right_only"):
        bad_merge_count = merged_df[merge_column].value_counts().get(bad_merge, 0)
        if bad_merge_count:
            warnings.warn(
                f"There are {bad_merge_count} '{bad_merge}' rows in the merged data", MergeWarning
            )
            bad_merge_found = True

    if not bad_merge_found:
        logger.info("The merge was healthy.")

    if keep_merge:
        return merged_df

    merged_df = merged_df.drop(columns=merge_column)

    return merged_df


def join_datasets(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: Union[str, List[str]],
    right_on: Union[str, List[str]],
    how: MergeHow = "left",
    check_merge: Union[bool, Literal["keep"]] = True,
    indicator_override: Optional[str] = None,
    **merge_kwargs,
) -> pd.DataFrame:
    """
    Join two datasets together.

    Parameters
    ----------
    left : pd.DataFrame
        The left dataset to join.
    right : pd.DataFrame
        The right dataset to join.
    left_on : Union[str, List[str]]
        The column to join on in the left dataset.
    right_on : Union[str, List[str]]
        The column to join on in the right dataset.
    how : MergeHow, optional
        The type of join to perform, by default "inner"
    check_merge : Union[bool, Literal["keep"]], optional
        Whether to check the merge for issues, by default True. If "keep" is passed, the merge
        column will be kept in the merged DataFrame.
    indicator_override : Optional[str], optional
        Override the indicator parameter in the merge function, by default None
    merge_kwargs : dict
        Additional keyword arguments to pass to the pandas.merge function.

    Returns
    -------
    pd.DataFrame
        The joined dataset.

    Raises
    ------
    MergeColumnsNotFoundError
        If the columns to join on are not found in the datasets. Reports which columns are missing.
    """
    logger.info(f"Joining the datasets on {left_on} and {right_on}")

    indicator = False
    if check_merge:
        indicator = indicator_override or True

    try:
        merged_data = pd.merge(
            left=left,
            right=right,
            left_on=left_on,
            right_on=right_on,
            how=how,
            indicator=indicator,
            **merge_kwargs,
        )
    except KeyError as e:
        raise MergeColumnsNotFoundError(left.columns, right.columns, left_on, right_on) from e

    if check_merge:
        keep_merge = check_merge == "keep"
        merged_data = check_merge_health(
            merged_data, merge_column=indicator_override, keep_merge=keep_merge
        )

    return merged_data
