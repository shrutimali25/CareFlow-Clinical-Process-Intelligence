"""
Time Features and Sequence Engineering Module
Calculates elapsed minutes, prior event timestamps, event sequences, and transition gaps.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
from src.data.loader import load_event_log, save_event_log, get_column_mapping


def compute_time_features(
    input_csv_path: Union[str, Path],
    output_csv_path: Union[str, Path]
) -> Dict[str, Any]:
    """
    Enriches the cleaned event log with sequential transition times.
    
    New features added:
    - previous_activity: Name of the activity immediately preceding this event.
    - previous_event_time: Timestamp of the preceding event in the case.
    - elapsed_minutes: Minutes elapsed since the previous event (NaN for first event).
    - event_sequence_nr: 1-indexed chronological position of the event in the patient case.
    
    Audits:
    - Verifies strictly non-negative elapsed times (elapsed_minutes >= 0).
    - Verifies monotonic increasing order for all patient traces.
    """
    input_file = Path(input_csv_path)
    output_file = Path(output_csv_path)

    print(f"[Time Features] Loading cleaned data from {input_file.name}...")
    df = load_event_log(input_file, parse_timestamps=True)
    case_col, act_col, time_col = get_column_mapping(df)

    # Ensure stable chronological sorting
    df = df.sort_values(by=[case_col, time_col], kind="stable").reset_index(drop=True)

    # 1. Event sequence number within each case
    df["event_sequence_nr"] = df.groupby(case_col).cumcount() + 1

    # 2. Previous event time and activity within case
    df["previous_event_time"] = df.groupby(case_col)[time_col].shift(1)
    df["previous_activity"] = df.groupby(case_col)[act_col].shift(1)

    # 3. Elapsed minutes between consecutive events
    df["elapsed_minutes"] = (
        (df[time_col] - df["previous_event_time"]).dt.total_seconds() / 60.0
    ).round(4)

    # 4. Check for negative elapsed times
    negative_elapsed_count = int((df["elapsed_minutes"] < 0).sum())
    if negative_elapsed_count > 0:
        raise ValueError(
            f"Data integrity error: Found {negative_elapsed_count} events with negative elapsed time!"
        )

    # 5. Monotonic ordering verification per case
    monotonic_increasing = df.groupby(case_col)[time_col].apply(
        lambda s: s.is_monotonic_increasing
    )
    cases_in_order = int(monotonic_increasing.sum())
    cases_out_of_order = int((~monotonic_increasing).sum())

    save_event_log(df, output_file)

    metrics = {
        "total_events": len(df),
        "unique_cases": int(df[case_col].nunique()),
        "first_events_count": int(df["previous_event_time"].isna().sum()),
        "negative_elapsed_times": negative_elapsed_count,
        "cases_in_chronological_order": cases_in_order,
        "cases_out_of_chronological_order": cases_out_of_order,
        "mean_elapsed_minutes": float(df["elapsed_minutes"].mean(skipna=True)),
        "median_elapsed_minutes": float(df["elapsed_minutes"].median(skipna=True)),
        "max_elapsed_minutes": float(df["elapsed_minutes"].max(skipna=True)),
        "has_case_NA": bool("NA" in df[case_col].values),
        "case_NA_event_count": int((df[case_col] == "NA").sum())
    }

    print(f"[Time Features] Calculation completed successfully!")
    print(f"  - Total events processed: {metrics['total_events']:,}")
    print(f"  - Unique patient cases: {metrics['unique_cases']:,}")
    print(f"  - Initial case events (no predecessor): {metrics['first_events_count']:,}")
    print(f"  - Cases strictly chronological: {metrics['cases_in_chronological_order']:,} / {metrics['unique_cases']:,}")
    print(f"  - Negative elapsed times: {metrics['negative_elapsed_times']}")
    print(f"  - Patient 'NA' preserved: {metrics['has_case_NA']} ({metrics['case_NA_event_count']} events)")
    print(f"  - Saved to: {output_file}")

    return metrics


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    with_times_csv = project_root / "data" / "processed" / "sepsis_with_times.csv"
    compute_time_features(cleaned_csv, with_times_csv)
