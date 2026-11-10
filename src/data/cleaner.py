"""
Data Cleaning and Standardization Module
Cleans event log, standardizes timestamps, preserves genuine clinical repetitions,
and guarantees case ID 'NA' preservation.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
from src.data.loader import load_event_log, save_event_log, get_column_mapping


def clean_event_log(
    input_csv_path: Union[str, Path],
    output_csv_path: Union[str, Path]
) -> Dict[str, Any]:
    """
    Cleans raw CSV event data while strictly preserving clinical data integrity.
    
    Cleaning rules applied:
    1. Preserves case ID 'NA' as a valid string identifier.
    2. Drops only rows with missing/null case IDs.
    3. Drops only rows with missing/null activities.
    4. Converts timestamps to timezone-aware UTC datetime.
    5. Drops rows with unparseable timestamps.
    6. Performs stable chronological sorting by [case_id, timestamp].
    7. Preserves identical timestamp occurrences (e.g. repeated lab tests like CRP/Leucocytes)
       which represent legitimate hospital repeat assays, NOT technical bugs.
    
    Returns:
        Dict of cleaning metrics and audit checks.
    """
    input_file = Path(input_csv_path)
    output_file = Path(output_csv_path)

    print(f"[Data Cleaning] Loading raw event log from {input_file.name}...")
    df = load_event_log(input_file, parse_timestamps=False)
    case_col, act_col, time_col = get_column_mapping(df)

    initial_rows = len(df)
    initial_cases = df[case_col].nunique()

    # 1. Check & handle missing case IDs
    missing_cases_count = int(df[case_col].isna().sum())
    if missing_cases_count > 0:
        print(f"  [Warning] Dropping {missing_cases_count} rows with missing case ID")
        df = df.dropna(subset=[case_col]).copy()

    # 2. Check & handle missing activities
    missing_acts_count = int(df[act_col].isna().sum())
    if missing_acts_count > 0:
        print(f"  [Warning] Dropping {missing_acts_count} rows with missing activity")
        df = df.dropna(subset=[act_col]).copy()

    # 3. Standardize timestamps to UTC
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    invalid_time_count = int(df[time_col].isna().sum())
    if invalid_time_count > 0:
        print(f"  [Warning] Dropping {invalid_time_count} rows with unparseable timestamp")
        df = df.dropna(subset=[time_col]).copy()

    # 4. Check repeated events at identical timestamps (Clinical Re-assays)
    dup_timestamp_events = int(df.duplicated(subset=[case_col, act_col, time_col], keep=False).sum())
    exact_duplicate_rows = int(df.duplicated().sum())

    # 5. Stable chronological sort by case and timestamp
    df = df.sort_values(by=[case_col, time_col], kind="stable").reset_index(drop=True)

    # 6. Save verified cleaned data
    save_event_log(df, output_file)

    metrics = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(df),
        "unique_cases": int(df[case_col].nunique()),
        "unique_activities": int(df[act_col].nunique()),
        "missing_cases_removed": missing_cases_count,
        "missing_activities_removed": missing_acts_count,
        "invalid_timestamps_removed": invalid_time_count,
        "exact_duplicate_rows_preserved": exact_duplicate_rows,
        "repeated_events_at_same_timestamp": dup_timestamp_events,
        "has_case_NA": bool("NA" in df[case_col].values),
        "case_NA_event_count": int((df[case_col] == "NA").sum())
    }

    print(f"[Data Cleaning] Cleaning completed successfully!")
    print(f"  - Cleaned events: {metrics['cleaned_rows']:,} (from {metrics['initial_rows']:,})")
    print(f"  - Unique cases: {metrics['unique_cases']:,}")
    print(f"  - Unique activities: {metrics['unique_activities']}")
    print(f"  - Case 'NA' preserved: {metrics['has_case_NA']} ({metrics['case_NA_event_count']} events)")
    print(f"  - Repeated events preserved: {metrics['repeated_events_at_same_timestamp']}")
    print(f"  - Saved to: {output_file}")

    return metrics


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    raw_csv = project_root / "data" / "processed" / "sepsis_event_log.csv"
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    clean_event_log(raw_csv, cleaned_csv)
