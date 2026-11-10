"""
Dataset Loading and I/O Module
Ensures safe loading of event logs without corrupted identifiers (e.g., preserving 'NA').
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import pandas as pd


# Default standard column names for process mining and analytics
CASE_COL = "case:concept:name"
ACTIVITY_COL = "concept:name"
TIMESTAMP_COL = "time:timestamp"


def get_column_mapping(df: pd.DataFrame) -> Tuple[str, str, str]:
    """
    Identifies the case, activity, and timestamp columns from a DataFrame.
    Supports both XES standard names and business friendly aliases.
    """
    case_candidates = [CASE_COL, "Case_ID", "case_id", "Patient_ID", "case"]
    activity_candidates = [ACTIVITY_COL, "Activity", "activity_name", "activity"]
    time_candidates = [TIMESTAMP_COL, "Timestamp", "timestamp", "time"]

    case_col = next((c for c in case_candidates if c in df.columns), None)
    act_col = next((c for c in activity_candidates if c in df.columns), None)
    time_col = next((c for c in time_candidates if c in df.columns), None)

    if not case_col:
        raise KeyError(f"Case identifier column not found. Checked: {case_candidates}")
    if not act_col:
        raise KeyError(f"Activity column not found. Checked: {activity_candidates}")
    if not time_col:
        raise KeyError(f"Timestamp column not found. Checked: {time_candidates}")

    return case_col, act_col, time_col


def load_event_log(
    file_path: Union[str, Path],
    parse_timestamps: bool = True
) -> pd.DataFrame:
    """
    Safely loads an event log CSV file.
    
    CRITICAL: Uses keep_default_na=False and na_values=[''] to ensure that
    valid patient case IDs such as 'NA' are NOT converted to NaN/missing values.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Event log file does not exist: {path}")

    # Explicitly treat case ID and activity as strings
    df = pd.read_csv(
        path,
        keep_default_na=False,
        na_values=[""],
        dtype={
            CASE_COL: str,
            "Case_ID": str,
            ACTIVITY_COL: str,
            "Activity": str
        }
    )

    if parse_timestamps:
        _, _, time_col = get_column_mapping(df)
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce", utc=True)

    return df


def save_event_log(
    df: pd.DataFrame,
    output_path: Union[str, Path]
) -> Path:
    """
    Safely exports a DataFrame to CSV, ensuring parent directories exist.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
