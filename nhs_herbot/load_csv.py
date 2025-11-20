"""
Module for loading CSV data into pandas DataFrames with custom error handling and logging.

This module provides functionality to load CSV data into pandas DataFrames, with support for
custom NA values and logging. It also includes custom exceptions for handling cases where
no file path or datasets are provided.

Classes
NoFilePathProvidedError(Exception)
NoDatasetsProvidedError(Exception)

Functions
---------
load_csv_data(dataset_name: str, **read_csv_kwargs) -> pd.DataFrame
load_devices_datasets(datasets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]

Constants
---------
NA_VALUES : list
    A list of strings representing custom NA values to be used when loading CSV data.
DATASETS : dict
    A dictionary containing dataset names and their corresponding file paths and read_csv arguments.

"""

from typing import Any

from loguru import logger
import pandas as pd
import tqdm

from nhs_herbot.errors import NoDatasetsProvidedError, NoFilePathProvidedError


def load_csv_data(dataset_name: str, **read_csv_kwargs) -> pd.DataFrame:
    """
    Load CSV data into a pandas DataFrame.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset being loaded.
    **read_csv_kwargs : dict
        Additional keyword arguments to pass to `pd.read_csv`. Must include `filepath_or_buffer`.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the loaded CSV data.

    Raises
    ------
    NoFilePathProvidedError
        If `filepath_or_buffer` is not provided in `read_csv_kwargs`.

    Notes
    -----
    This function logs the dataset name and file path before loading the data.
    """
    try:
        filepath_or_buffer = read_csv_kwargs["filepath_or_buffer"]
    except KeyError as e:
        raise NoFilePathProvidedError("No file path provided.") from e

    logger.info(f"Loading {dataset_name} data from: {filepath_or_buffer}")

    return pd.read_csv(
        skip_blank_lines=True,
        **read_csv_kwargs,
    ).dropna(how="all")


def load_devices_datasets(
    datasets: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Load device datasets from CSV files.

    Parameters
    ----------
    datasets : dict of dict
        A dictionary where the key is the dataset name (str) and the value is another dictionary
        containing keyword arguments to be passed to the `load_csv_data` function.

    Returns
    -------
    dict of dict
        The input dictionary with an additional key "data" in each inner dictionary,
        containing the loaded DataFrame.

    Raises
    ------
    NoDatasetsProvidedError
        If the `datasets` dictionary is empty.

    Notes
    -----
    The `load_csv_data` function is expected to be defined elsewhere and should handle the
    actual loading of the CSV data based on the provided keyword arguments.
    """
    if not datasets:
        raise NoDatasetsProvidedError("No datasets provided.")

    for dataset_name, dataset_kwargs in tqdm.tqdm(datasets.items(), desc="Loading datasets"):
        if "data" in dataset_kwargs:
            dataset_kwargs.pop("data")
        dataset_df = load_csv_data(dataset_name, **dataset_kwargs)
        datasets[dataset_name]["data"] = dataset_df

    return datasets
