"""
Tests for nhs_herbot/data_in/load_csv.py
"""

import pandas as pd
import pytest

from nhs_herbot import (
    NoDatasetsProvidedError,
    NoFilePathProvidedError,
    load_csv_data,
    load_datasets,
)


@pytest.fixture
def mock_read_csv(mocker):
    return mocker.patch("nhs_herbot.pd.read_csv")


class TestLoadCsvData:
    """
    Tests for load_csv_data
    """

    def test_read_csv_called_once(self, mock_read_csv):
        """
        Test that the read csv function is called once
        """
        load_csv_data("test", filepath_or_buffer="test")
        mock_read_csv.assert_called_once()

    def test_read_csv_called_with_args(self, mock_read_csv, mocker):
        """
        Test that the read csv function is called with the expected arguments
        """
        expected_na_values = [""]
        expected_skip_blank_lines = True
        expected_filepath_or_buffer = "test"

        load_csv_data("test", filepath_or_buffer="test", na_values=expected_na_values)
        mock_read_csv.assert_called_with(
            na_values=expected_na_values,
            skip_blank_lines=expected_skip_blank_lines,
            filepath_or_buffer=expected_filepath_or_buffer,
        )

    def test_return_type(self, mock_read_csv):
        """
        Test that the function returns a pandas DataFrame
        """
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df
        result = load_csv_data("test", filepath_or_buffer="test")
        assert isinstance(result, pd.DataFrame)

    def test_return_shape(self, mock_read_csv):
        """
        Test that the function returns a DataFrame with the expected shape
        """
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df
        result = load_csv_data("test", filepath_or_buffer="test")
        assert result.shape == (2, 2)

    def test_assert_error(self):
        """
        Test that the function raises an AssertionError when no file path is provided
        """
        with pytest.raises(NoFilePathProvidedError):
            load_csv_data("test")

    def test_logger_called(self, mock_info, mock_read_csv):
        """
        Test that the logger is called with the expected message
        """
        load_csv_data("test", filepath_or_buffer="test")
        mock_info.assert_called_with("Loading test data from: test")


class TestLoadDeviceDatasets:
    """
    Tests for load_datasets
    """

    def test_load_devices_datasets(self, mock_read_csv):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        result = load_datasets(datasets)
        assert set(result.keys()) == set(datasets.keys())

    def test_data(self, mock_read_csv):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        result = load_datasets(datasets)
        for dataset in result.values():
            assert "data" in dataset

    def test_data_shape(self, mock_read_csv):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        result = load_datasets(datasets)
        for dataset in result.values():
            assert dataset["data"].shape == (2, 2)

    def test_data_type(self, mock_read_csv):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        result = load_datasets(datasets)
        for dataset in result.values():
            assert isinstance(dataset["data"], pd.DataFrame)

    def test_no_datasets_error(self):
        """
        Test that the function raises an AssertionError when no datasets are provided
        """
        with pytest.raises(NoDatasetsProvidedError):
            load_datasets({})

    def test_removes_data(self, mock_read_csv):
        """
        Test that the function removes the "data" key from the datasets dictionary
        and then overwrites it with the loaded DataFrame
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1", "data": "test_data"},
        }

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        result = load_datasets(datasets)
        dataset = result["test1"]
        assert str(dataset["data"]) != "test_data"


if __name__ == "__main__":
    pytest.main([__file__])
