"""
Tests for nhs_herbot/joins.py
"""

from contextlib import nullcontext

from loguru import logger
import pandas as pd
import pytest

from nhs_herbot import MergeColumnsNotFoundError, MergeWarning, joins

# from nhs_herbot import processing


class TestCheckMergeHealth:
    """
    Tests for joins.check_merge
    """

    @pytest.fixture
    def merged_df(self):
        """
        Return a merged DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["col1", "col2", "_merge"],
            data=[
                ("foo", "bar", "both"),
                ("baz", "qux", "left_only"),
                ("quux", "corge", "right_only"),
            ],
        )

    @pytest.fixture
    def empty_merged_df(self):
        """
        Return an empty merged DataFrame for testing.
        """
        return pd.DataFrame(columns=["col1", "col2", "_merge"])

    def test_no_merge_column(self, mocker, merged_df):
        """
        Test that the function returns the merged DataFrame if the merge column is not found.
        """
        input_df = merged_df.drop(columns="_merge")
        mock_logger = mocker.spy(logger, "info")
        actual = joins.check_merge_health(input_df)

        pd.testing.assert_frame_equal(actual, input_df)
        mock_logger.assert_called_once_with(
            "The merge column, _merge, was not found in the merged dataframe"
        )

    def test_empty_input_with_columns(self, mocker, empty_merged_df):
        """
        Test that the function drops the merge column and returns an empty DataFrame when passed a
        DataFrame with no rows. The logger should also be called, reporting that the merge was
        healthy.
        """
        input_df = empty_merged_df
        expected_df = pd.DataFrame(columns=["col1", "col2"])
        mock_logger = mocker.spy(logger, "info")

        actual = joins.check_merge_health(input_df)

        pd.testing.assert_frame_equal(actual, expected_df)
        mock_logger.assert_called_once_with("The merge was healthy.")

    @pytest.mark.parametrize(
        "keep_index, bad_merge_message, expected",
        [
            (
                1,
                "There are 1 'left_only' rows in the merged data",
                pd.DataFrame(columns=["col1", "col2"], data=[("baz", "qux")]),
            ),
            (
                2,
                "There are 1 'right_only' rows in the merged data",
                pd.DataFrame(columns=["col1", "col2"], data=[("quux", "corge")]),
            ),
        ],
    )
    def test_bad_merge_found_warning_message(
        self, merged_df, keep_index, bad_merge_message, expected
    ):
        """
        Test that the function raises a MergeWarning when a bad merge is found with the expected
        message.
        """
        input_df = merged_df.iloc[[keep_index], :].copy(deep=True).reset_index(drop=True)
        with pytest.warns(MergeWarning, match=bad_merge_message):
            actual = joins.check_merge_health(input_df)

        pd.testing.assert_frame_equal(actual, expected)

    def test_bad_merge_found_warning_called_twice(self, mocker, merged_df):
        """
        Test that the function raises a warning the correct number of times when a bad merge is
        found.
        """
        mock_warn = mocker.patch("nhs_herbot.warnings.warn")

        joins.check_merge_health(merged_df)

        assert mock_warn.call_count == 2

    def test_bad_merge_no_info(self, mocker, merged_df):
        """
        Test that the function raises a warning when a bad merge is found.
        """
        mock_info = mocker.spy(logger, "info")

        with pytest.warns(MergeWarning):
            joins.check_merge_health(merged_df)

        mock_info.assert_not_called()

    def test_keep_merge(self, merged_df):
        """
        Test that the function keeps the merge column when `keep_merge` is True.
        """
        expected = merged_df
        with pytest.warns(MergeWarning):
            actual = joins.check_merge_health(merged_df, keep_merge=True)

        pd.testing.assert_frame_equal(actual, expected)

    def test_merge_column_none(self, merged_df):
        """
        Test that the function uses the default merge column when `merge_column` is None.
        """
        expected = merged_df.drop(columns="_merge")

        with pytest.warns(MergeWarning):
            actual = joins.check_merge_health(merged_df, merge_column=None)

        pd.testing.assert_frame_equal(actual, expected)

    def test_different_merge_column(self, empty_merged_df):
        """
        Test that the function uses the specified merge column when `merge_column` is provided.
        """
        input_df = empty_merged_df.rename(columns={"_merge": "test"})
        expected = pd.DataFrame(columns=["col1", "col2"])

        actual = joins.check_merge_health(input_df, merge_column="test")

        pd.testing.assert_frame_equal(actual, expected)


class TestJoinDatasets:
    """
    Tests for joins.join_datasets
    """

    @pytest.fixture
    def left(self):
        """
        Return a left DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["col1", "col2"],
            data=[("foo", "bar"), ("baz", "qux"), ("ping", "pong")],
        )

    @pytest.fixture
    def right(self):
        """
        Return a right DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["col3", "col4"],
            data=[("foo", "bar"), ("baz", "qux"), ("bing", "bong")],
        )

    def test_returns_dataframe(self, left, right):
        """
        Test that the function returns a DataFrame.
        """
        with pytest.warns(MergeWarning):
            actual = joins.join_datasets(left, right, left_on="col1", right_on="col3")
        assert isinstance(actual, pd.DataFrame)

    def test_default_merge(self, left, right):
        """
        Test that the function performs a left merge by default.
        """
        expected = pd.DataFrame(
            columns=["col1", "col2", "col3", "col4"],
            data=[
                ("foo", "bar", "foo", "bar"),
                ("baz", "qux", "baz", "qux"),
                ("ping", "pong", None, None),
            ],
        )
        with pytest.warns(MergeWarning):
            actual = joins.join_datasets(left, right, left_on="col1", right_on="col3")

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "how, expected",
        [
            (
                "right",
                pd.DataFrame(
                    columns=["col1", "col2", "col3", "col4"],
                    data=[
                        ("foo", "bar", "foo", "bar"),
                        ("baz", "qux", "baz", "qux"),
                        (None, None, "bing", "bong"),
                    ],
                ),
            ),
            (
                "outer",
                pd.DataFrame(
                    columns=["col1", "col2", "col3", "col4"],
                    data=[
                        ("foo", "bar", "foo", "bar"),
                        ("baz", "qux", "baz", "qux"),
                        ("ping", "pong", None, None),
                        (None, None, "bing", "bong"),
                    ],
                ),
            ),
            (
                "inner",
                pd.DataFrame(
                    columns=["col1", "col2", "col3", "col4"],
                    data=[("foo", "bar", "foo", "bar"), ("baz", "qux", "baz", "qux")],
                ),
            ),
        ],
    )
    def test_other_merges(self, left, right, how, expected):
        """
        Test that the function performs the specified merge type. Cases include:
        - right
        - outer
        - inner

        Cases not included:
        - left as it is the default and tested in test_default_merge
        """
        actual = joins.join_datasets(
            left, right, left_on="col1", right_on="col3", how=how, check_merge=False
        )

        actual = actual.sort_values(by=["col1", "col2", "col3", "col4"]).reset_index(drop=True)
        expected = expected.sort_values(by=["col1", "col2", "col3", "col4"]).reset_index(drop=True)

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "kwarg, expected",
        [
            ("merge_column", None),
            ("keep_merge", False),
        ],
    )
    def test_check_merge_defaults_kwargs(self, left, right, mocker, kwarg, expected):
        """
        Test that the function checks the merge health by default with the correct args.
        """
        mock_check_merge = mocker.spy(joins, "check_merge_health")

        with pytest.warns(MergeWarning):
            joins.join_datasets(left, right, left_on="col1", right_on="col3")

        actual_call_args = mock_check_merge.call_args
        actual_args = actual_call_args.args
        actual_kwargs = actual_call_args.kwargs

        assert isinstance(actual_args[0], pd.DataFrame)
        assert actual_kwargs[kwarg] == expected

    @pytest.mark.parametrize(
        "check_merge, expected",
        [
            (True, False),
            ("keep", True),
        ],
    )
    def test_check_merge_keep(self, left, right, mocker, check_merge, expected):
        """
        Test that the correct value is passed to `keep_merge` of check_merge_health function when
        `check_merge` arg is provided. Cases include:
        - True - Should be False
        - "keep" - Should be True

        Cases not included:
        - False - check_merge_health function should not be called and is tested in
        test_check_merge_not_called
        """
        mock_check_merge = mocker.spy(joins, "check_merge_health")

        with pytest.warns(MergeWarning):
            joins.join_datasets(
                left, right, left_on="col1", right_on="col3", check_merge=check_merge
            )

        actual_call_args = mock_check_merge.call_args
        actual_kwargs = actual_call_args.kwargs

        assert actual_kwargs["keep_merge"] is expected

    def test_check_merge_not_called(self, left, right, mocker):
        """
        Test that the function does not call check_merge_health when `check_merge` is False.
        """
        mock_check_merge = mocker.spy(joins, "check_merge_health")

        joins.join_datasets(left, right, left_on="col1", right_on="col3", check_merge=False)

        mock_check_merge.assert_not_called()

    @pytest.mark.parametrize(
        "check_merge, indicator_override, expected_merge, expected_check_merge",
        [
            (True, None, True, None),
            (True, "test", "test", "test"),
            ("keep", None, True, None),
            ("keep", "test", "test", "test"),
            (False, None, False, "not called"),
            (False, "test", False, "not called"),
        ],
    )
    def test_check_indicator_override(
        self,
        left,
        right,
        mocker,
        check_merge,
        indicator_override,
        expected_merge,
        expected_check_merge,
    ):
        """
        Test that the function uses the specified merge column when `indicator_override` is provided.

        Note: We only check for the MergeWarning when check_merge is True or "keep". This is because
        the warning is raised in the check_merge_health function, which is not called when
        check_merge is False. `nullcontext` is used to skip the warning check in the conditional
        context statement.
        """
        mock_merge = mocker.spy(pd, "merge")
        mock_check_merge = mocker.spy(joins, "check_merge_health")

        with pytest.warns(MergeWarning) if check_merge else nullcontext():
            joins.join_datasets(
                left,
                right,
                left_on="col1",
                right_on="col3",
                check_merge=check_merge,
                indicator_override=indicator_override,
            )

        actual_merge_kwargs = mock_merge.call_args.kwargs
        assert actual_merge_kwargs["indicator"] == expected_merge

        if check_merge:
            actual_check_merge_kwargs = mock_check_merge.call_args.kwargs
            assert actual_check_merge_kwargs["merge_column"] == expected_check_merge
        else:
            mock_check_merge.assert_not_called()

    def test_logging(self, left, right, mocker):
        """
        Test that the function logs the correct message.
        """
        mock_logger = mocker.spy(logger, "info")

        with pytest.warns(MergeWarning):
            joins.join_datasets(left, right, left_on="col1", right_on="col3")

        mock_logger.assert_called_once_with("Joining the datasets on col1 and col3")

    def test_error_when_no_on_columns(self, left, right):
        """
        Test that the function raises a MergeColumnsNotFoundError when the columns are not found in the
        dataset.
        """
        with pytest.raises(MergeColumnsNotFoundError):
            joins.join_datasets(left, right, left_on=["test"], right_on=["test"])


if __name__ == "__main__":
    pytest.main([__file__])
