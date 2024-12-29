import pandas as pd
import numpy as np


def fc32(series_or_value, decimals=5):
    """Handle both Series and scalar inputs."""
    assert decimals >= 0 and decimals <= 5, "Decimals must be between 0 and 5"
    if isinstance(series_or_value, pd.Series):
        return series_or_value.round(decimals).astype("float32")
    else:
        return round(series_or_value, decimals)


def required_column_check(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Check if the required columns are present in the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame to check.
        required_columns (list): The list of required columns to check.

    Returns:
        bool: True if all required columns are present in the DataFrame.

    Raises:
        KeyError: If any of the required columns are missing in the input DataFrame.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if len(missing_columns) > 0:
        raise KeyError(f"Required columns {missing_columns} not found in DataFrame.")
    return True


def calendar_calculations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate calendar-related values based on the given DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing the required columns.

    Returns:
        pd.DataFrame: The input DataFrame with additional calculated columns.

    Raises:
        KeyError: If any of the required columns are missing in the input DataFrame.
    """
    required_column_check(df, ["mark_back", "mark_front", "strike", "underlying"])

    df["calCost"] = fc32(df["mark_back"] - df["mark_front"])
    df["calGapPct"] = fc32(df["calCost"] / df["mark_front"])
    df["undPricePctDiff"] = fc32((df["strike"] - df["underlying"]) / df["underlying"])
    df["calCostPct"] = fc32((df["calCost"] / df["underlying"]) * 100)
    return df


def calculate_fb_spread(df: pd.DataFrame, fb: str) -> pd.DataFrame:
    """
    Calculate the spread and spread percentage for the specified front or back columns.

    Args:
        df (pd.DataFrame): The input DataFrame containing the required columns.
        fb (str): The identifier for front or back columns. Must be either 'front' or 'back'.

    Returns:
        pd.DataFrame: The input DataFrame with additional calculated columns.

    Raises:
        AssertionError: If the 'fb' argument is not either 'front' or 'back'.
        KeyError: If any of the required columns are missing in the input DataFrame.
    """
    assert fb in ["front", "back"], "fb must be either 'front' or 'back'"
    required_column_check(df, [f"ask_{fb}", f"bid_{fb}", f"mark_{fb}"])
    # if not all(col in df.columns for col in required_columns):
    #     raise KeyError(f"Required columns {required_columns} not found in DataFrame.")

    df[f"spread_{fb}"] = df[f"ask_{fb}"] - df[f"bid_{fb}"]
    df[f"spreadPct_{fb}"] = (df[f"spread_{fb}"] / df[f"mark_{fb}"]).round(2)
    return df


def calculate_cal_spread(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the calendar spread and spread percentage.

    Args:
        df (pd.DataFrame): The input DataFrame containing the required columns.

    Returns:
        pd.DataFrame: The input DataFrame with additional calculated columns.

    Raises:
        KeyError: If any of the required columns are missing in the input DataFrame.
    """
    required_column_check(df, ["bid_front", "ask_back", "ask_front", "bid_back"])

    # ask_cal should be larger than bid_cal
    df["ask_cal"] = fc32(df["ask_back"] - df["bid_front"])

    # bid_cal should be smaller than ask_cal
    df["bid_cal"] = fc32(df["bid_back"] - df["ask_front"])

    df["spread_cal"] = fc32(df["ask_cal"] - df["bid_cal"])
    df["mark_cal"] = fc32((df["bid_cal"] + df["ask_cal"]) / 2)

    # Handle division by zero for spreadPct_cal
    # TODO: Handle division by zero for spreadPct_cal
    df["spreadPct_cal"] = df.apply(
        lambda row: np.nan if row["mark_cal"] == 0 else row["spread_cal"] / row["mark_cal"],
        axis=1,
    )
    df["spreadPct_cal"] = fc32(df["spreadPct_cal"])
    return df


def calculate_mark(df: pd.DataFrame) -> pd.DataFrame:
    required_column_check(df, ["ask", "bid"])
    df["mark"] = fc32(((df["ask"] - df["bid"]) / 2) + df["bid"], decimals=2)
    return df


def calculate_mark_fb(df: pd.DataFrame, fb: str) -> pd.DataFrame:
    assert fb in ["front", "back"], "fb must be either 'front' or 'back'"
    required_column_check(df, [f"ask_{fb}", f"bid_{fb}"])
    df[f"mark_{fb}"] = fc32(((df[f"ask_{fb}"] - df[f"bid_{fb}"]) / 2) + df[f"bid_{fb}"], decimals=2)
    return df


def pct_under_over_mean(df: pd.DataFrame) -> pd.DataFrame:
    assert any(
        ["implied_vol_front" in df.columns, "implied_vol_back" in df.columns]
    ), "Missing implied volatility columns"
    if "histcalcostmean" in df.columns:
        df["pct_under_over_mean"] = df["calCostPct"] - df["histcalcostmean"]
    else:
        df["pct_under_over_mean"] = df["calCostPct"] - df["calCostPctMean"]
    return df


def iv_pct_diff(df):
    required_column_check(df, ["implied_vol_front", "implied_vol_back"])

    # Calculate iv_pct_diff with conditions for zero values
    def calculate_iv_pct_diff_nested(row):
        if row["implied_vol_front"] == 0:
            # Return 0 if both values are zero, 100% otherwise
            return 0 if row["implied_vol_back"] == 0 else 1.0
        else:
            # Calculate the percentage difference
            return (row["implied_vol_front"] - row["implied_vol_back"]) / row["implied_vol_front"]

    df["iv_pct_diff"] = df.apply(calculate_iv_pct_diff_nested, axis=1)
    df["iv_pct_diff"] = fc32(df["iv_pct_diff"])
    return df


def calculate_diffs(df: pd.DataFrame) -> pd.DataFrame:
    df = iv_pct_diff(df)
    df = pct_under_over_mean(df)
    return df


def calculate_spreads(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the spreads and spread percentages for front, back, and calendar columns.

    Args:
        df (pd.DataFrame): The input DataFrame containing the required columns.

    Returns:
        pd.DataFrame: The input DataFrame with additional calculated columns.

    Raises:
        AssertionError: If the 'fb' argument is not either 'front' or 'back'.
        KeyError: If any of the required columns are missing in the input DataFrame.
    """
    df = calculate_fb_spread(df, "front")
    df = calculate_fb_spread(df, "back")
    df = calculate_cal_spread(df)
    return df
