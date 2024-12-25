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
            "strike": [120, 180],
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
            base_sample_df, ["mark_back", "mark_front", "strike", "underlying"]
        )
        is True
    )


def test_required_column_check_missing_columns(base_sample_df):
    with pytest.raises(KeyError):
        oe.required_column_check(
            base_sample_df,
            ["mark_back", "mark_front", "strike", "underlying", "invalid"],
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


# Test calculate_cal_spread
def test_calculate_cal_spread(base_sample_df):
    df = base_sample_df.copy()
    df["ask_cal"] = df["bid_front"] - df["ask_back"]
    df["bid_cal"] = df["ask_front"] - df["bid_back"]
    df["mark_cal"] = (df["ask_cal"] + df["bid_cal"]) / 2
    df = oe.calculate_cal_spread(df)
    assert "ask_cal" in df.columns
    assert "bid_cal" in df.columns
    assert "spread_cal" in df.columns
    assert "spreadPct_cal" in df.columns


def test_calculate_cal_spread_division_by_zero():
    # Generate 50 rows with edge cases and valid scenarios
    # Includes zeros every 5 rows
    df = pd.DataFrame(
        {
            "bid_front": [50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
            "ask_back": [50, 46, 47, 53, 49, 50, 51, 52, 53, 59],
            "ask_front": [55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
            "bid_back": [45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
        }
    )

    df = oe.calculate_cal_spread(df)
    zeros = df[df["ask_cal"] == 0].shape[0]
    assert df["spreadPct_cal"].isna().sum() == zeros, "Division by zero not handled"


# Test calculate_spreads
def test_calculate_spreads(base_sample_df):
    df = base_sample_df.copy()
    df["ask_cal"] = df["bid_front"] - df["ask_back"]
    df["bid_cal"] = df["ask_front"] - df["bid_back"]
    df["mark_cal"] = (df["ask_cal"] + df["bid_cal"]) / 2
    df = oe.calculate_spreads(df)
    assert "spread_front" in df.columns
    assert "spreadPct_front" in df.columns
    assert "spread_back" in df.columns
    assert "spreadPct_back" in df.columns
    assert "ask_cal" in df.columns
    assert "spread_cal" in df.columns
    assert "spreadPct_cal" in df.columns
