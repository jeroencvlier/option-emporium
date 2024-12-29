import pandas as pd
import numpy as np
import pytest
import option_emporium as oe


# Fixture for base sample DataFrame
@pytest.fixture
def base_sample_df():
    return pd.DataFrame(
        {
            "mark_back": [100, 200],
            "mark_front": [50, 150],
            "strike_relative": [120, 180],
            "underlying": [100, 175],
            "ask_front": [55, 160],
            "bid_front": [45, 140],
            "ask_back": [105, 210],
            "bid_back": [95, 190],
        }
    )


# Test fc32
def test_fc32():
    series = pd.Series([1.234567, 2.345678, 3.456789])
    result = oe.fc32(series)
    expected = np.array([1.23457, 2.34568, 3.45679], dtype=np.float32)
    assert result.dtype == "float32"
    assert np.allclose(result.values, expected, atol=1e-5)


def test_required_column_check(base_sample_df):
    assert (
        oe.required_column_check(
            base_sample_df, ["mark_back", "mark_front", "strike_relative", "underlying"]
        )
        is True
    )


def test_required_column_check_missing_columns(base_sample_df):
    with pytest.raises(KeyError):
        oe.required_column_check(
            base_sample_df,
            ["mark_back", "mark_front", "strike_relative", "underlying", "invalid"],
        )


# Test calendar_calculations
def test_calendar_calculations(base_sample_df):
    df = oe.calendar_calculations(base_sample_df)
    assert "calCost" in df.columns
    assert "calGapPct" in df.columns
    assert "undPricePctDiff" in df.columns
    assert "calCostPct" in df.columns
    assert df["calCost"].dtype == "float32"
    assert df["calGapPct"].dtype == "float32"
    assert df["undPricePctDiff"].dtype == "float32"
    assert df["calCostPct"].dtype == "float32"


def test_calendar_calculations_missing_columns():
    df = pd.DataFrame({"mark_back": [100, 200], "mark_front": [50, 150]})
    with pytest.raises(KeyError):
        oe.calendar_calculations(df)


# Test calculate_fb_spread
def test_calculate_fb_spread(base_sample_df):
    df = oe.calculate_fb_spread(base_sample_df, "front")
    assert "spread_front" in df.columns
    assert "spreadPct_front" in df.columns


def test_calculate_fb_spread_invalid_fb(base_sample_df):
    with pytest.raises(AssertionError):
        oe.calculate_fb_spread(base_sample_df, "invalid")


def test_calculate_fb_spread_missing_columns():
    df = pd.DataFrame({"ask_front": [55], "bid_front": [45]})
    with pytest.raises(KeyError):
        oe.calculate_fb_spread(df, "front")


def test_calculate_cal_spread_division_by_zero():
    """
    Test that calculate_cal_spread correctly handles division by zero
    and returns NaN in spreadPct_cal when midpoint is zero.
    """
    df = pd.read_csv("tests/test_calculate_cal_spread_division_by_zero.csv")

    ground_truth = df[["ask_cal", "bid_cal", "spread_cal", "mark_cal", "spreadPct_cal"]].copy()
    for col in ground_truth.columns:
        ground_truth[col] = oe.fc32(df[col])

    df = oe.calculate_cal_spread(df)

    # df.info()
    # ground_truth.info()

    assert df["ask_cal"].equals(ground_truth["ask_cal"]), "ask_cal not calculated correctly"
    assert df["bid_cal"].equals(ground_truth["bid_cal"]), "bid_cal not calculated correctly"
    assert df["spread_cal"].equals(
        ground_truth["spread_cal"]
    ), "spread_cal not calculated correctly"
    assert df["mark_cal"].equals(ground_truth["mark_cal"]), "mark_cal not calculated correctly"
    assert df["spreadPct_cal"].equals(
        ground_truth["spreadPct_cal"]
    ), "spreadPct_cal not calculated correctly"
